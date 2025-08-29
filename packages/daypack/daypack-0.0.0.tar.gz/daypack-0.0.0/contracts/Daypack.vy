# @version 0.4.3
"""
@title Daypack
@license Apache-2.0
@author ApeWorX LTD.
"""
NAME: constant(String[7]) = "Daypack"
NAMEHASH: constant(bytes32) = keccak256(NAME)
# NOTE: Update this before each release (controls EIP712 Domain)
VERSION: public(constant(String[10])) = "0.1"
VERSIONHASH: constant(bytes32) = keccak256(VERSION)

EIP712_DOMAIN_TYPEHASH: constant(bytes32) = keccak256(
    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
)
UPDATE_TYPEHASH: constant(bytes32) = keccak256(
    "Update(uint256 action,bytes calldata)"
)
EXECUTE_TYPEHASH: constant(bytes32) = keccak256(
    "Execute(address target,uint256 value,bytes calldata)"
)

# NOTE: This will be used by upgradeable proxy for delegation
IMPLEMENTATION: public(address)

num_signers: public(uint256)
is_signer: public(HashMap[address, bool])
threshold: public(uint256)

flag ActionType:
    UPGRADE_IMPLEMENTATION
    ROTATE_SIGNERS
    CONFIGURE_MODULE
    SET_ADMIN_GUARD
    SET_EXECUTE_GUARD
    # NOTE: Add future reconfiguration actions here

interface IAdminGuard:
    def preUpdateCheck(target: address, action: ActionType, calldata: Bytes[65535]): nonpayable
    def postUpdateCheck(): nonpayable

admin_guard: public(IAdminGuard)

interface IExecuteGuard:
    def preExecuteCheck(target: address, eth_value: uint256, calldata: Bytes[65535]): nonpayable
    def postExecuteCheck(): nonpayable

execute_guard: public(IExecuteGuard)

module_enabled: public(HashMap[address, bool])


# NOTE: Future variables (used for core features) must be added below here


# NOTE: All admin events are separated out
event ImplementationUpgraded:
    executor: indexed(address)
    old: indexed(address)
    new: indexed(address)


event SignersRotated:
    executor: indexed(address)
    signers_added: DynArray[address, 11]
    signers_removed: DynArray[address, 11]


event ModuleUpdated:
    executor: indexed(address)
    module: indexed(address)
    enabled: indexed(bool)


event AdminGuardUpdated:
    executor: indexed(address)
    old: indexed(IAdminGuard)
    new: indexed(IAdminGuard)


event ExecuteGuardUpdated:
    executor: indexed(address)
    old: indexed(IExecuteGuard)
    new: indexed(IExecuteGuard)


event Execution:
    executor: indexed(address)
    success: indexed(bool)
    target: indexed(address)
    eth_value: uint256
    calldata: Bytes[65535]


# NOTE: IERC5267
@view
@external
def eip712Domain() -> (
    bytes1,
    String[50],
    String[20],
    uint256,
    address,
    bytes32,
    DynArray[uint256, 32],
):
    return (
        # NOTE: `0x0f` equals `01111` (`salt` is not used)
        0x0f,
        NAME,
        VERSION,
        chain.id,
        self,
        empty(bytes32),
        empty(DynArray[uint256, 32]),  # No extensions
    )


@external
def initialize(signers: DynArray[address, 11], threshold: uint256):
    assert self.threshold == 0  # dev: can only initialize once
    assert threshold > 0 and threshold <= len(signers)

    for signer: address in signers:
        self.is_signer[signer] = True

    self.num_signers = len(signers)
    self.threshold = threshold


def _verify_signatures(msghash: bytes32, signatures: DynArray[Bytes[65], 11]):
    assert len(signatures) >= self.threshold

    already_approved: DynArray[address, 11] = []
    for sig: Bytes[65] in signatures:
        # NOTE: Signatures should be 65 bytes in RSV order
        r: bytes32 = convert(slice(sig, 0, 32), bytes32)
        s: bytes32 = convert(slice(sig, 32, 32), bytes32)
        v: uint8 = convert(slice(sig, 64, 1), uint8)
        signer: address = ecrecover(msghash, v, r, s)
        assert self.is_signer[signer]
        assert signer not in already_approved
        already_approved.append(signer)


def _hash_typed_data_v4(struct_hash: bytes32) -> bytes32:
    domain_separator: bytes32 = keccak256(
        abi_encode(EIP712_DOMAIN_TYPEHASH, NAMEHASH, VERSIONHASH, chain.id, self)
    )
    return keccak256(concat(x"1901", domain_separator, struct_hash))


def _rotate_signers(
    signers_to_add: DynArray[address, 11],
    signers_to_rm: DynArray[address, 11],
    threshold: uint256,
):
    num_signers: uint256 = self.num_signers

    for signer: address in signers_to_rm:
        assert self.is_signer[signer]
        self.is_signer[signer] = False
        num_signers -= 1

    for signer: address in signers_to_add:
        assert not self.is_signer[signer]
        self.is_signer[signer] = True
        num_signers += 1

    if threshold > 0:
        self.threshold = threshold

    assert self.threshold <= num_signers
    self.num_signers = num_signers


@external
def update(
    action: ActionType,
    calldata: Bytes[65535],
    signatures: DynArray[Bytes[65], 11],
):
    msghash: bytes32 = self._hash_typed_data_v4(
        keccak256(abi_encode(UPDATE_TYPEHASH, action, calldata))
    )
    self._verify_signatures(msghash, signatures)

    admin_guard: IAdminGuard = self.admin_guard
    if admin_guard.address != empty(address):
        extcall admin_guard.preUpdateCheck(self, action, calldata)

    if action == ActionType.UPGRADE_IMPLEMENTATION:
        new: address = abi_decode(calldata, address)
        log ImplementationUpgraded(executor=msg.sender, old=self.IMPLEMENTATION, new=new)
        self.IMPLEMENTATION = new

    elif action == ActionType.ROTATE_SIGNERS:
        signers_to_add: DynArray[address, 11] = []
        signers_to_rm: DynArray[address, 11] = []
        threshold: uint256 = 0
        signers_to_add, signers_to_rm, threshold = abi_decode(
            calldata,
            (DynArray[address, 11], DynArray[address, 11], uint256),
        )
        self._rotate_signers(signers_to_add, signers_to_rm, threshold)
        log SignersRotated(
            executor=msg.sender,
            signers_added=signers_to_add,
            signers_removed=signers_to_rm,
        )

    elif action == ActionType.CONFIGURE_MODULE:
        module: address = empty(address)
        enabled: bool = False
        module, enabled = abi_decode(calldata, (address, bool))
        self.module_enabled[module] = enabled
        log ModuleUpdated(executor=msg.sender, module=module, enabled=enabled)

    elif action == ActionType.SET_ADMIN_GUARD:
        # NOTE: Don't use `admin_guard` as it would override above
        guard: IAdminGuard = abi_decode(calldata, IAdminGuard)
        log AdminGuardUpdated(executor=msg.sender, old=self.admin_guard, new=guard)
        self.admin_guard = guard

    elif action == ActionType.SET_EXECUTE_GUARD:
        guard: IExecuteGuard = abi_decode(calldata, IExecuteGuard)
        log ExecuteGuardUpdated(executor=msg.sender, old=self.execute_guard, new=guard)
        self.execute_guard = guard

    else:
        raise "Unsupported"

    if admin_guard.address != empty(address):
        # NOTE: We use the old admin guard to execute the check
        extcall admin_guard.postUpdateCheck()


@external
def execute(
    target: address,
    eth_value: uint256,
    calldata: Bytes[65535],
    signatures: DynArray[Bytes[65], 11] = [],
):
    if not self.module_enabled[msg.sender]:
        msghash: bytes32 = self._hash_typed_data_v4(
            keccak256(abi_encode(EXECUTE_TYPEHASH, target, eth_value, calldata))
        )
        self._verify_signatures(msghash, signatures)

    guard: IExecuteGuard = self.execute_guard
    if guard.address != empty(address):
        extcall guard.preExecuteCheck(target, eth_value, calldata)

    # NOTE: No delegatecalls allowed (cannot modify configuration this way)
    success: bool = raw_call(target, calldata, value=eth_value, revert_on_failure=False)
    log Execution(
        executor=msg.sender,
        success=success,
        target=target,
        eth_value=eth_value,
        calldata=calldata,
    )

    if guard.address != empty(address):
        extcall guard.postExecuteCheck()
