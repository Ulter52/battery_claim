# Battery Claim

A comprehensive Battery Warranty Management application for ERPNext designed to manage the complete lifecycle of battery warranty claims—from customer claim registration to manufacturer settlement.

---

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/Ulter52/battery_claim.git --branch develop
bench install-app battery_claim
```



# Version

**Current Release:** `v1.0.0`

---

# Overview

Battery Claim extends ERPNext by providing a structured warranty workflow for batteries.

Unlike the traditional Project-based approach, V1 introduces a dedicated Battery Warranty Claim document that acts as the **single source of truth** for the complete warranty lifecycle.

The application manages:

- Customer warranty claims
- Manufacturer approval
- Replacement issue to customer
- Dispatch of defective batteries
- Receipt of manufacturer replacement
- Credit Note settlement

---

# Features

## Battery Warranty Claim

Central document managing the complete warranty lifecycle.

Features:

- Customer details
- Battery details
- Warranty verification
- Claim tracking
- Replacement tracking
- Supplier settlement
- Credit Note support

---

## Warranty Approval

Records manufacturer approval.

Stores:

- Approval Number
- Approval Date
- Supplier
- Approved Item Code
- Cancellation Reason
- Amendment History

Automatically updates Battery Warranty Claim.

---

## Delivery Note Integration

Creates Delivery Note directly from Battery Warranty Claim.

Automatically:

- Issues approved battery
- Captures issued Serial Number
- Updates Battery Warranty Claim

---

## Warranty Claim Batch

Groups multiple warranty claims for dispatch to manufacturers.

Stores:

- Dispatch Date
- Manufacturer
- Warehouse
- Claim Snapshot

Automatically updates Battery Warranty Claim.

---

## Purchase Receipt Integration

Creates Purchase Receipt when replacement battery is received from supplier.

Automatically updates:

- Received Item
- Received Serial Number
- Claim Status

---

## Credit Note Support

Supports settlement through Credit Note without replacement battery.

This follows an independent workflow and directly closes the claim.

---

# Workflow

## Replacement Workflow

```
Battery Warranty Claim
          │
          ▼
Warranty Approval
          │
          ▼
Delivery Note
          │
          ▼
Warranty Claim Batch
          │
          ▼
Purchase Receipt
          │
          ▼
Closed
```

---

## Supplier First Workflow

```
Battery Warranty Claim
          │
          ▼
Warranty Approval
          │
          ▼
Warranty Claim Batch
          │
          ▼
Purchase Receipt
          │
          ▼
Stock Received
          │
          ▼
Delivery Note
          │
          ▼
Closed
```

---

## Credit Note Workflow

```
Battery Warranty Claim
          │
          ▼
Warranty Approval
          │
          ▼
Credit Note
          │
          ▼
Closed
```

---

# Claim Status

| Status | Description |
|----------|------------|
| Approval Pending | Waiting for manufacturer approval |
| Approved | Claim approved by manufacturer |
| Replaced | Replacement battery issued to customer |
| Dispatched | Defective battery dispatched to manufacturer |
| Stock Received | Manufacturer replacement received, waiting for customer replacement |
| Closed | Warranty claim completed |
| Rejected | Claim rejected by manufacturer |
| Cancelled | Claim cancelled |

---

# DocType Responsibilities

## Battery Warranty Claim

Acts as the **master document**.

Responsible for:

- Warranty workflow
- Customer information
- Battery information
- Claim status
- Linked documents

---

## Warranty Approval

Responsible for:

- Manufacturer approval
- Approved Item Code
- Supplier
- Approval Number

---

## Delivery Note

Responsible for:

- Customer replacement
- Issued Item
- Issued Serial Number

---

## Warranty Claim Batch

Responsible for:

- Dispatch management
- Manufacturer shipment
- Dispatch snapshot

---

## Purchase Receipt

Responsible for:

- Manufacturer replacement receipt
- Received Item
- Received Serial Number

---

# Business Rules

## Warranty Approval

- One approval per claim.
- Approval is mandatory before replacement.
- Approved Item Code becomes default replacement item.
- Supplier is captured during approval.

---

## Delivery Note

- Cannot be created before approval.
- Cannot be created for Credit Note claims.
- Uses Approved Item Code by default.

---

## Warranty Claim Batch

- Only claims with Delivery Note can be dispatched.
- Captures claim snapshot.
- Dispatch updates claim lifecycle.

---

## Purchase Receipt

- Supplier replacement can arrive before customer replacement.
- Received Item defaults from Approved Item Code.
- User may change item before submission if supplier provides different replacement.

---

## Credit Note

- Independent settlement workflow.
- No Delivery Note.
- No Purchase Receipt.
- Directly closes claim.

---

# Design Principles

The application follows the following principles.

## Single Source of Truth

Battery Warranty Claim owns the complete warranty lifecycle.

Every downstream document only updates Battery Warranty Claim.

---

## Event Driven

Business events update the master document.

Examples:

- Warranty Approval
- Delivery Note
- Warranty Claim Batch
- Purchase Receipt

---

## Server Side Validation

Business validations always execute on the server.

Client-side code is used only for user experience.

---

## Snapshot Philosophy

Warranty Claim Batch stores claim information as a snapshot.

Historical dispatch data remains unchanged even if Battery Warranty Claim changes later.

---

## Lifecycle Driven UI

Available actions are determined by the Lifecycle Engine.

The client never decides which action is allowed.

---

# Technical Architecture

```
Battery Warranty Claim
        │
        ▼
Lifecycle Engine
        │
        ├──────────────┐
        │              │
Warranty Approval   Delivery Note
        │              │
        ▼              ▼
Warranty Claim Batch
        │
        ▼
Purchase Receipt
```

The Lifecycle Engine controls:

- Create buttons
- View buttons
- Available actions

Business documents never communicate directly with each other.

All communication occurs through Battery Warranty Claim.

---

# Architecture Philosophy

Every document owns only its own responsibility.

```
Battery Warranty Claim
    owns Workflow

Warranty Approval
    owns Approval

Delivery Note
    owns Customer Replacement

Warranty Claim Batch
    owns Dispatch

Purchase Receipt
    owns Manufacturer Settlement
```

This architecture minimizes coupling and keeps each document independent.

---

# Folder Structure

```
battery_claim/

├── api/
│   └── battery_warranty_claim_wrapper.py
│
├── battery_claim/
│   ├── doctype/
│   │
│   ├── battery_warranty_claim/
│   ├── warranty_approval/
│   ├── warranty_claim_batch/
│   │
│   └── ...
│
├── events/
│   ├── delivery_note.py
│   ├── purchase_receipt.py
│   └── ...
│
├── utils/
│   ├── lifecycle.py
│   ├── stock.py
│   └── ...
│
├── patches/
│   └── v1_0/
│
├── hooks.py
└── README.md
```

---

# Module Architecture

```
                  Battery Warranty Claim
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
Warranty Approval    Delivery Note   Warranty Claim Batch
                                               │
                                               ▼
                                       Purchase Receipt
```

Battery Warranty Claim is the central document.

All downstream documents update only Battery Warranty Claim.

No document directly updates another document.

---

# Lifecycle Engine

The Lifecycle Engine determines available user actions.

Responsibilities:

- Create Buttons
- View Buttons
- Workflow availability

Examples:

```
Create Warranty Approval

Create Delivery Note

Create Purchase Receipt

Add to Warranty Claim Batch

View Linked Documents
```

The Lifecycle Engine does **not** update documents.

It only determines which actions are currently available.

---

# Event Architecture

Every ERP document owns only its own event.

```
Warranty Approval

on_submit()

↓

Update Battery Warranty Claim

on_cancel()

↓

Rollback Battery Warranty Claim
```

The same pattern is used by:

- Delivery Note
- Warranty Claim Batch
- Purchase Receipt

This provides predictable behaviour throughout the application.

---

# Client Side Architecture

Client scripts are responsible only for:

- User Interface
- Button Visibility
- Serial Lookup
- Read-only Behaviour

Business validation is never performed on the client.

---

# Server Side Architecture

Python controls:

- Business Rules
- Validation
- Workflow
- Status Updates
- Linked Document Updates

This guarantees consistency regardless of whether the document is created through:

- ERPNext UI
- REST API
- Data Import
- Background Jobs

---

# Validation Strategy

Validation occurs at multiple levels.

## Battery Warranty Claim

- Serial validation
- Duplicate warranty claim prevention
- Customer information
- Warranty eligibility

---

## Warranty Approval

- Duplicate approval number
- Claim status validation
- Approved Item validation
- Supplier validation

---

## Delivery Note

- Approved Item validation
- Warehouse validation
- Replacement validation

---

## Warranty Claim Batch

- Claim snapshot validation
- Duplicate dispatch prevention

---

## Purchase Receipt

- Supplier validation
- Received serial validation
- Replacement validation

---

# Status Calculation

Claim Status represents the current stage of the warranty lifecycle.

```
Approval Pending

↓

Approved

↓

Replaced

↓

Dispatched

↓

Stock Received

↓

Closed
```

The order of document creation may vary.

The application always calculates the correct status based on linked documents.

---

# Snapshot Design

Warranty Claim Batch stores a snapshot of the claim at dispatch time.

Example:

```
Battery Warranty Claim

↓

Warranty Claim Batch Item

Defective Item

Issued Item

Issued Serial

Remarks
```

Even if the Battery Warranty Claim changes later, the dispatch history remains unchanged.

---

# Integration

Battery Claim integrates with standard ERPNext documents.

Supported Documents:

- Delivery Note
- Purchase Receipt
- Serial No
- Customer
- Supplier
- Item
- Warehouse

No standard ERPNext DocTypes are modified.

---

# Installation

Install the application.

```
bench get-app battery_claim
```

Install on site.

```
bench --site sitename install-app battery_claim
```

Run migration.

```
bench --site sitename migrate
```

Build assets.

```
bench build
```

Restart services.

```
bench restart
```

---

# Migration Notes

Version 1 introduces Battery Warranty Claim as the central document.

Previous Project-based workflow has been retired.

Migration includes:

- Warranty Claim Batch update
- Snapshot migration
- Legacy compatibility
- Data migration patches

Migration patches are designed to be idempotent wherever possible.

---

# Development Guidelines

When adding new functionality:

✓ Update Battery Warranty Claim only.

Avoid updating downstream documents.

---

Every new event should follow this structure.

```
on_submit()

↓

Update Battery Warranty Claim

↓

on_cancel()

↓

Rollback Battery Warranty Claim
```

Maintain this pattern throughout the application.

---

# Coding Standards

Python

- Small focused functions
- Single Responsibility Principle
- No duplicated business logic
- Server-side validation

JavaScript

- UI only
- No business validation
- Helper functions
- Lifecycle-driven buttons

---

# Release Notes

## v1.0.0

Initial Production Release.

### Added

- Battery Warranty Claim
- Warranty Approval
- Delivery Note Integration
- Warranty Claim Batch
- Purchase Receipt Integration
- Credit Note Workflow
- Lifecycle Engine
- Snapshot Architecture

### Improved

- Event-driven workflow
- Cleaner document responsibilities
- Automatic document linking
- Better validation
- Cleaner UI

### Removed

- Project-based workflow
- Duplicate status updates
- Legacy dispatch dependency

---

# Roadmap

## Version 1.x

- Production bug fixes
- Minor UI improvements
- Additional reports
- Print format enhancements

---

## Version 2

Planned improvements:

- Dispatch Voucher rename
- Dashboard
- Timeline View
- Analytics
- Manufacturer Portal
- Mobile Enhancements
- Service Centre Integration
- Shared Status Engine
- Shared Document Update Service

---

# Contributing

Before contributing:

- Follow project coding standards.
- Keep business logic on the server.
- Avoid duplicate validation.
- Keep JavaScript limited to presentation.
- Update documentation whenever functionality changes.

---

# License

Copyright (c) 2026  
Dhirendra Sharma and Contributors

Released under the MIT License.

---

# Acknowledgements

This application was developed to provide a structured, scalable and maintainable Battery Warranty Management workflow for ERPNext.

Special emphasis has been placed on:

- Clean Architecture
- Single Source of Truth
- Event-driven Design
- Maintainability
- Future Scalability

Battery Warranty Claim v1.0.0 represents the first production-ready release of the application and establishes the architectural foundation for future versions.

### License

mit
