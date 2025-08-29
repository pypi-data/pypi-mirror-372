# @version 0.4.3
"""
@title DaypackProxy
@license Apache-2.0
@author ApeWorX LTD.
"""

IMPLEMENTATION: address
# NOTE: NO OTHER VARIABLES ALLOWED


@deploy
def __init__(
    implementation: address,
    signers: DynArray[address, 11],
    threshold: uint256,
):
    self.IMPLEMENTATION = implementation
    raw_call(
        implementation,
        abi_encode(signers, threshold, method_id=method_id("initialize(bytes,uint256)")),
        is_delegate_call=True,
    )


@payable
@external
def __default__():
    if msg.value == 0:
        success: bool = raw_call(
            self.IMPLEMENTATION,
            msg.data,
            is_delegate_call=True,
            revert_on_failure=False,
        )
    # else: Accept ether (do nothing)
