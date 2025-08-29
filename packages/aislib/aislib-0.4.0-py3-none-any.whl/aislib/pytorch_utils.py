from sympy import Symbol
from sympy.solvers import solve
from torch import nn


def calc_size_after_conv_sequence(
    input_width: int, input_height: int, conv_sequence: nn.Sequential
) -> tuple[int, int]:
    current_width = input_width
    current_height = input_height
    for block_index, block in enumerate(conv_sequence):
        conv_operations = [i for i in vars(block)["_modules"] if i.find("conv") != -1]

        for operation_index, operation in enumerate(conv_operations):
            conv_layer = vars(block)["_modules"][operation]

            padded_height = current_height + 2 * conv_layer.padding[0]
            padded_width = current_width + 2 * conv_layer.padding[1]
            if any(
                k > s
                for k, s in zip(
                    conv_layer.kernel_size,
                    (padded_height, padded_width),
                    strict=False,
                )
            ):
                raise ValueError(
                    f"Kernel size of layer "
                    f"{block_index}.{operation_index} ({operation}) "
                    f"exceeds padded input size in one or more dimensions. "
                    f"Original input size (hxw): {current_height}x{current_width} "
                    f"(this is likely the source of the problem, especially if "
                    f"error layer is conv_1). "
                    f"Padded input size became (hxw): {padded_height}x{padded_width}. "
                    f"Kernel size: {conv_layer.kernel_size}. "
                    "Please adjust the kernel size to ensure the it "
                    "does not exceed the padded input size for each dimension."
                )

            new_width = _calc_layer_output_size_for_axis(
                size=current_width, layer=conv_layer, axis=1
            )
            new_height = _calc_layer_output_size_for_axis(
                size=current_height, layer=conv_layer, axis=0
            )

            if int(new_width) == 0 or int(new_height) == 0:
                kernel_size = conv_layer.kernel_size
                stride = conv_layer.stride
                padding = conv_layer.padding
                dilation = conv_layer.dilation

                raise ValueError(
                    f"Calculated size after convolution sequence is 0 for layer "
                    f"{block_index}.{operation_index} ({operation}). "
                    f"Input size (hxw): {current_height}x{current_width}. "
                    f"Convolution parameters: kernel size = {kernel_size}, "
                    f"stride = {stride}, padding = {padding}, dilation = {dilation}. "
                    "Please adjust these parameters to ensure they are appropriate "
                    "for the input size."
                )

            current_width, current_height = new_width, new_height

    return int(current_width), int(current_height)


def _calc_layer_output_size_for_axis(size: int, layer: nn.Module, axis: int):
    kernel_size = layer.kernel_size[axis]
    padding = layer.padding[axis]
    stride = layer.stride[axis]
    dilation = layer.dilation[axis]

    output_size = conv_output_formula(
        input_size=size,
        padding=padding,
        dilation=dilation,
        kernel_size=kernel_size,
        stride=stride,
    )

    return output_size


def calc_conv_params_needed(
    input_size: int, kernel_size: int, stride: int, dilation: int
) -> tuple[int, int]:
    if input_size < 0:
        raise ValueError("Got negative size for input width: %d", input_size)

    target_size = conv_output_formula(
        input_size=input_size,
        padding=0,
        dilation=dilation,
        kernel_size=kernel_size,
        stride=stride,
    )
    for k_size in [kernel_size, kernel_size - 1, kernel_size + 1]:
        for t_size in [target_size, target_size - 1, target_size + 1]:
            padding = _solve_for_padding(
                input_size=input_size,
                target_size=t_size,
                dilation=dilation,
                stride=stride,
                kernel_size=k_size,
            )

            if padding is not None:
                assert isinstance(padding, int)
                return k_size, padding

    raise AssertionError(
        f"Could not find a solution for padding with the supplied conv "
        f"parameters: {locals()}."
    )


def conv_output_formula(
    input_size: int, padding: int, dilation: int, kernel_size: int, stride: int
) -> int:
    out_size = (
        input_size + 2 * padding - dilation * (kernel_size - 1) - 1
    ) // stride + 1
    return out_size


def _solve_for_padding(
    input_size: int, target_size: int, dilation: int, stride: int, kernel_size: int
) -> int | None:
    p = Symbol("p", integer=True, nonnegative=True)
    padding = solve(
        ((input_size + (2 * p) - dilation * (kernel_size - 1) - 1) / stride + 1)
        - target_size,
        p,
    )

    if len(padding) > 0:
        return int(padding[0])

    return None
