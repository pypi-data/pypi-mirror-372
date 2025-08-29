from collections.abc import Callable, Generator

import torch
import torch.nn.functional as F
from torch.nn import Module
from torch.nn.parameter import Parameter


class Swish(Module):
    __constants__ = ["num_parameters"]

    def __init__(self, num_parameters=1, init=1):
        self.num_parameters = num_parameters
        super().__init__()
        self.weight = Parameter(
            torch.Tensor(num_parameters).fill_(init), requires_grad=True
        )

    def forward(self, input_):
        return input_ * torch.sigmoid(self.weight * input_)

    def extra_repr(self):
        return f"num_parameters={self.num_parameters}"


class Mish(Module):
    """
    Applies the mish function element-wise:
    mish(x) = x * tanh(softplus(x)) = x * tanh(ln(1 + exp(x)))
    Shape:
        - Input: (N, *) where * means, any number of additional
          dimensions
        - Output: (N, *), same shape as the input
    Examples:
        >>> m = Mish()
        >>> input = torch.randn(2)
        >>> output = m(input)
    """

    def __init__(self):
        """
        Init method.
        """
        super().__init__()

    def forward(self, input):
        """
        Forward pass of the function.
        """
        return mish(input)


@torch.jit._script_if_tracing
def mish(input):
    """
    Applies the mish function element-wise:
    mish(x) = x * tanh(softplus(x)) = x * tanh(ln(1 + exp(x)))
    See additional documentation for mish class.
    """
    return input * torch.tanh(F.softplus(input))


class AdaHessian(torch.optim.Optimizer):
    def __init__(
        self,
        params: torch.Tensor,
        lr: float = 0.1,
        betas: tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0.0,
        hessian_power: float = 1.0,
        auto_hessian: bool = True,
        update_each: int = 1,
    ):
        """
        From: https://github.com/davda54/ada-hessian
        """

        if not lr >= 0.0:
            raise ValueError(f"Invalid learning rate: {lr}")
        if not eps >= 0.0:
            raise ValueError(f"Invalid epsilon value: {eps}")
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError(f"Invalid beta parameter at index 0: {betas[0]}")
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError(f"Invalid beta parameter at index 1: {betas[1]}")
        if not 0.0 <= hessian_power <= 1.0:
            raise ValueError(f"Invalid Hessian power value: {hessian_power}")
        if not auto_hessian and update_each > 1:
            raise ValueError(
                f"Delayed hessian update is not supported for manual updates, "
                f"delay: {update_each}"
            )

        self.update_each = update_each
        self.auto_hessian = auto_hessian

        # use a separate generator that deterministically generates the same `z`s
        # across all GPUs in case of distributed training
        self.generator = torch.Generator().manual_seed(2147483647)

        defaults = {
            "lr": lr,
            "betas": betas,
            "eps": eps,
            "weight_decay": weight_decay,
            "hessian_power": hessian_power,
        }
        super().__init__(params, defaults)

        for p in self.get_params():
            p.hess = 0.0
            self.state[p]["hessian step"] = 0

    def get_params(self) -> Generator[torch.Tensor, None, None]:
        return (
            p for group in self.param_groups for p in group["params"] if p.requires_grad
        )

    def zero_hessian(self) -> None:
        for p in self.get_params():
            if (
                not isinstance(p.hess, float)
                and self.state[p]["hessian step"] % self.update_each == 0
            ):
                p.hess.zero_()

    @torch.no_grad()
    def set_hessian(self) -> None:
        params = []
        for p in filter(lambda p: p.grad is not None, self.get_params()):
            if (
                self.state[p]["hessian step"] % self.update_each == 0
            ):  # compute the trace only each `update_each` step
                params.append(p)
            self.state[p]["hessian step"] += 1

        if len(params) == 0:
            return

        if (
            self.generator.device != params[0].device
        ):  # hackish way of casting the generator to the right device
            self.generator = torch.Generator(params[0].device).manual_seed(2147483647)

        grads = [p.grad for p in params]
        zs = [
            torch.randint(0, 2, p.size(), generator=self.generator, device=p.device)
            * 2.0
            - 1.0
            for p in params
        ]  # Rademacher distribution {-1.0, 1.0}

        h_zs = torch.autograd.grad(
            grads, params, grad_outputs=zs, only_inputs=True, retain_graph=False
        )
        for h_z, z, p in zip(h_zs, zs, params, strict=False):
            p.hess += h_z * z  # enable accumulating hessians

    @torch.no_grad()
    def step(self, closure: Callable = None) -> torch.Tensor:
        loss = None
        if closure is not None:
            loss = closure()

        if self.auto_hessian:
            self.zero_hessian()
            self.set_hessian()

        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None or p.hess is None:
                    continue

                # Perform correct stepweight decay as in AdamW
                p.mul_(1 - group["lr"] * group["weight_decay"])

                state = self.state[p]

                # State initialization
                if len(state) == 1:
                    state["step"] = 0
                    state["exp_avg"] = torch.zeros_like(
                        p.data
                    )  # Exponential moving average of gradient values
                    state["exp_hessian_diag_sq"] = torch.zeros_like(
                        p.data
                    )  # Exponential moving average of Hessian diagonal square values

                exp_avg, exp_hessian_diag_sq = (
                    state["exp_avg"],
                    state["exp_hessian_diag_sq"],
                )
                beta1, beta2 = group["betas"]
                state["step"] += 1

                # Decay the first and second moment running average coefficient
                exp_avg.mul_(beta1).add_(p.grad, alpha=1 - beta1)
                exp_hessian_diag_sq.mul_(beta2).addcmul_(
                    p.hess, p.hess, value=1 - beta2
                )

                bias_correction1 = 1 - beta1 ** state["step"]
                bias_correction2 = 1 - beta2 ** state["step"]

                k = group["hessian_power"]
                denom = (
                    (exp_hessian_diag_sq / bias_correction2)
                    .pow_(k / 2)
                    .add_(group["eps"])
                )

                # make update
                step_size = group["lr"] / bias_correction1
                p.addcdiv_(exp_avg, denom, value=-step_size)

        return loss


class LabelSmoothingLoss(Module):
    def __init__(self, classes: int, smoothing: float = 0.0, dim: int = -1):
        super().__init__()
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing
        self.cls = classes
        self.dim = dim

    def forward(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        input = input.log_softmax(dim=self.dim)
        with torch.no_grad():
            true_dist = torch.zeros_like(input)
            true_dist.fill_(self.smoothing / (self.cls - 1))
            true_dist.scatter_(1, target.data.unsqueeze(1), self.confidence)
        return torch.mean(torch.sum(-true_dist * input, dim=self.dim))
