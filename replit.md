# CivicConnect - Community Issue Tracker

## Overview

CivicConnect is a community issue tracking web application that enables citizens to report, track, and engage with local civic issues. The application provides a platform for users to submit issue reports, view community problems, and participate in a gamified system with leaderboards and badges. It includes separate interfaces for regular users and administrators, with admin capabilities for managing and moderating reported issues.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Single-page Application (SPA)**: Built as a complete self-contained HTML file with embedded CSS and JavaScript
- **Dynamic Content Rendering**: Uses JavaScript to dynamically switch between different views/pages without page reloads
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox for layout management
- **Component-based Structure**: Modular JavaScript functions for rendering different sections (login, dashboard, issues feed, etc.)

### Data Management
- **Client-side Storage**: Uses browser `localStorage` for data persistence, simulating a backend database
- **Data Models**: Structured data for users, issues, leaderboard points, and badges
- **Default Data Population**: Includes seed data for initial app state with sample issues and users

### User Interface Design
- **Design System**: Dark theme with blue/gray color palette using Poppins font family
- **Icon System**: Lucide icons for consistent visual elements
- **Interactive Elements**: Hover effects, smooth transitions, and dynamic form validation
- **Layout Structure**: Sidebar navigation with main content area for different application views

### Authentication & Authorization
- **Dual Login System**: Separate authentication flows for regular users and administrators
- **Role-based Access**: Different interface capabilities based on user type (user vs admin)
- **Session Management**: Uses localStorage to maintain login state across browser sessions

### Application Features
- **Issues Management**: Create, view, filter, and categorize community issues
- **Geolocation Integration**: Browser geolocation API for automatic location detection
- **Image Upload**: File handling for issue photo attachments with preview functionality
- **Gamification**: Points system, badges, and leaderboards to encourage user engagement
- **Filtering & Search**: Dynamic filtering of issues by category, status, and other criteria

## External Dependencies

### Third-party Libraries
- **Lucide Icons**: Icon library loaded via CDN for UI elements
- **Google Fonts**: Poppins font family for typography

### Browser APIs
- **localStorage**: For client-side data persistence
- **Geolocation API**: For automatic location detection when reporting issues
- **File API**: For handling image uploads and previews

### Hosting & Deployment
- **Static Hosting**: Designed as a single HTML file suitable for simple web hosting
- **No Backend Dependencies**: Self-contained application requiring only a web server for static file delivery