# Overview

Daypack: A rugged multisig wallet for everyday adventures

## Design

Daypack is a simple, yet flexible, multi-owner smart contract wallet designed for high-value, day-to-day activities.
It is designed to support multiple users (up to 11) working together to co-sign and execute important transactions.

Out of the box, Daypack is designed to be used via [`DaypackProxy`](./contracts/DaypackProxy),
which is a simple, upgradeable forwarding proxy that calls (via delegateproxy)
to a singleton deployment of [`Daypack`](./contracts/Daypack).
It is only designed to be used via the Proxy, as it is intended to be a long-term stateful contract containing important assets
that we don't want to lose when upgrading to a newer version of the code.

The singleton deployment is deployed once per chain and is used as that chain's official copy of that particular version.
The versioning of this repo matches the versioning of the deployments on-chain, where the git tag should match 1:1 to
the value of `VERSION()` on the singleton (as well as your personal proxy).

There are two types of EIP712 structures used within Daypack: `Update` and `Execute`.
They are designed to ensure that only important administrative updates occur via `Update`,
and common, non-admin transactions occur via `Execute`.
This is done to create a physical separation between critical, configuration-modifying transactions, and non-critical ones.
**It is highly recommended** to downstream signing infra that works w/ Daypack to create a clear UX distinction between
these two types of calls, making it clear that critical actions can impact the operational safety of Daypack.

> [!NOTE]
> The way that signatures are collected to be placed on-chain is out of scope for this specification.

Additionally, both types of transactions have "Guards" which are 3rd party contracts that should implement pre- and post-execution
checks on their respective transaction types.
Use cases for Guards can include (for admin `Update`s) adding timelocked update restrictions, blacklisting certain addresses,
or (for normal `Execute`s) adding per diem limits on asset transfers, restricting calls to certain contracts, etc.
Having two separate Guards, one for each transaction type, is useful because an `Execute` Guard being non-functional does
not represent an existential threat to the operation of the wallet, only with an `Update` Guard.
**This should encourage the use of Guards for proper operation of the wallet in day-to-day operational scenarios**,
increasing overall safety when using Daypack.

Finally, Daypack implements "Modules" which are contracts that can be enabled in the wallet (through an `Update` action)
that are allowed to bypass the signer signature check when commiting arbitrary `Execute` transactions.
This functionality is extremely useful for adding automation to your day-to-day operations, making your operation of the
wallet safer and less prone to social engineering exploits.

Technically, while it is possible to use Daypack for a "personal" multisig (where you own all the signers on the wallet),
it is suggested to make use of something like [`Purse`](https://github.com/fubuloubu/Purse) (with a secure cold wallet instead)
to add automation and advanced capabilities to your personal, high-valued wallets.

---

Daypack is inspired by [Safe Smart Account](https://github.com/safe-global/safe-smart-account).

## Contributing

This project is written in [Vyper](https://docs.vyperlang.org/en/stable).

This project uses [`ape`](https://apeworx.io/framework) to compile, test and script it.
See the [Installation Guide](https://docs.apeworx.io/ape/latest/userguides/quickstart#installation) for help installing it.
