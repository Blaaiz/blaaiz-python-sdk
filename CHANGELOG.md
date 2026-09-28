# Changelog

## [1.5.0](https://github.com/Blaaiz/blaaiz-python-sdk/compare/v1.4.0...v1.5.0) (2026-09-28)


### Features

* **oauth:** request the compliance-kyc scopes by default ([2073b93](https://github.com/Blaaiz/blaaiz-python-sdk/commit/2073b93160e7d8512877e957cb5c657665e69757))
* **oauth:** request the compliance-kyc:pii:read scope by default ([fd2b6e6](https://github.com/Blaaiz/blaaiz-python-sdk/commit/fd2b6e62430d73fa69b7fbff9e0931134a3cd77f))
* **signa:** add Signa merchant KYC session service ([6404e2c](https://github.com/Blaaiz/blaaiz-python-sdk/commit/6404e2cbab1ff853b80ede2ab26c29b362f42e30))
* **signa:** read captured applicant data and documents ([0fcf2cc](https://github.com/Blaaiz/blaaiz-python-sdk/commit/0fcf2cc948e57a1a60c8e1de5f5e2fcabf1a0918))

## 1.4.0 - 2026-08-28

This release brings the SDK up to date with the current Blaaiz API. All Blaaiz SDKs move to 1.4.0 together, so the same version means the same features in every language.

### Added
- Merchant reference on payouts and collections. Blaaiz saves it, returns it, and lets you find the transaction by it.
- Swaps: move money between two of your business wallets.
- Refunds: start a refund and get a refund.
- Rates: list the exchange rates for your business.
- Bank checks: verify a GBP account (payee) and a EUR IBAN.
- Interac money request: ask a payer for money by email.
- Business customer KYB: add and remove owners, upload owner ID files, upgrade to full KYB, and submit for review.
- Business customer documents: upload, list, get, update, and delete.

### Fixed
- Create a business customer without personal ID fields. The API does not allow them for a business.
- Upload customer files with the correct request method.
- Start a collection without the old, unused `currency` field.
- Update and replay a webhook on the correct address.
