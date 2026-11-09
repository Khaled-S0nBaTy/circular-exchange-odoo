# Circular Exchange (Odoo 17)

An Odoo addon for a circular materials exchange. It lets buyers publish material requests and suppliers publish available material listings, then connects compatible requests and listings through offers.

## Main workflow

1. Create material categories and material listings.
2. A buyer creates a material request. It starts in Draft and can be opened by the buyer.
3. The buyer searches for matching listings.
4. A supplier creates a Proposed offer from a matching listing.
5. The buyer accepts or rejects the offer. Accepted quantities update listing availability and the request's remaining quantity; a fully covered request becomes Fulfilled.

## Included models

- `material.category` — material categories.
- `material.list` — supplier listings and available quantities.
- `material.request` — buyer requests and remaining quantities.
- `material.offer` — proposed quantities linking a request to a listing.

## Requirements

- Odoo 17.0
- Odoo Community or Enterprise server with Python dependencies installed

## Installation

1. Place the `circular_exchange` addon directory in an Odoo addons path.
2. Restart the Odoo server.
3. Update the Apps list in Odoo, then install **Circular Exchange**.

For a local development setup, use your own Odoo configuration and database. Do not commit database credentials or local configuration files.

## Project status

A learning project. Matching, request, listing, and offer workflows have been developed and exercised locally; further review and testing may still be needed before production use.
