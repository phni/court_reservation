# Court Reservation System

A modern web application for managing court reservations and player assignments, built with Flask and Bootstrap.

## Features

- Create and manage court reservations
- Dynamic court and player management
- Mobile-friendly responsive design
- Dark mode interface
- Real-time player assignment
- Multiple courts handling

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/court_reservation.git
cd court_reservation
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Project Structure
court_reservation/
├── app/
│   ├── templates/
│   │   ├── base.html
│   │   ├── reservation_form.html
│   │   └── reservations_list.html
│   ├── models.py
│   ├── routes.py
│   └── __init__.py
├── migrations/
├── instance/
├── .gitignore
├── config.py
└── README.md

## Usage

1. Navigate to the homepage
2. Create a new reservation by specifying:
   - Reservation title
   - Number of courts
   - Players per court
   - Duration
3. Add players to each court
4. View and manage reservations through the reservations list

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask framework
- Bootstrap for UI components
- Contributors and maintainers