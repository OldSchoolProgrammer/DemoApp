# DemoApp - Jewelry Inventory Management System

A comprehensive Django-based inventory management system designed specifically for jewelry businesses. This application tracks stock, manages suppliers, and handles specialized jewelry attributes like metal type, weight, and gemstones.

## Features

### 💎 Inventory Management
- **Detailed Item Records**: Track items with jewelry-specific fields (Metal Type, Gemstone, Weight in grams).
- **Automatic SKU Generation**: Smart SKU generation based on category prefixes (e.g., `JWL-RIN-1001`).
- **Barcode Generation**: Automatically generates Code128 barcodes for each item upon creation.
- **Image Management**: Support for product images and auto-generated barcode images.

### 📦 Stock Control
- **Transaction Tracking**: Record stock movements (In, Out, Adjustments) with timestamps and user attribution.
- **Stock Status**: Real-time visual indicators for stock levels (Out, Low, OK).
- **Value Calculation**: Automatic calculation of stock value and profit margins.

### 🏭 Supplier & Category Management
- **Supplier Directory**: Manage vendor contact details and link them to inventory items.
- **Categorization**: Organize inventory into customizable categories (Rings, Necklaces, etc.).

### 💳 Sales & CRM (New)
- **Customer Records**: comprehensive customer management with purchase history.
- **Invoicing**: Create and manage professional invoices linked to inventory.
- **Stripe Integration**: Secure payment processing with auto-generated Payment Links.
- **Notifications**: Send invoices and paylinks directly via Email or SMS.

## Tech Stack

- **Backend**: Django 5.2, Python 3.x
- **Database**: SQLite (default) / Configurable
- **Imaging**: Pillow (for image processing and barcode generation)
- **Frontend**: Django Templates, Bootstrap 5 (via crispy-forms)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DemoApp
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Usage

1. Log in to the admin panel or the main application using your superuser credentials.
2. Create **Categories** and **Suppliers** first.
3. Add **Jewelry Items**. SKUs and Barcodes will be generated automatically.
4. Use the dashboard to view stock levels and manage inventory.
