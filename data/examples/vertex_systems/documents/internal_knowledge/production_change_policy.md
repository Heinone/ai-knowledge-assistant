# Production Change Policy

This policy applies to software and infrastructure changes affecting Vertex Systems production environments.

## Standard changes

Production changes require:

- a reviewed pull request
- passing automated tests
- a documented rollback plan
- approval from someone other than the change author

Changes must normally be deployed during the team's approved deployment window.

## High-risk changes

A high-risk change includes:

- database schema migrations
- authentication or authorization changes
- major infrastructure modifications
- changes affecting customer data storage

High-risk changes require approval from an Engineering Manager before deployment.

## Emergency changes

Emergency changes may bypass the normal deployment window when required to restore service or address an active security issue.

The on-call engineer may authorize an emergency deployment.

Emergency deployments must still have a rollback plan whenever technically possible.

A retrospective review of the emergency change must be completed within two business days.

## Friday deployments

Non-emergency high-risk production changes must not be deployed after 15:00 Helsinki time on Friday.

Exceptions require explicit approval from the Director of Engineering.