#!/usr/bin/env python3
"""
Simple HTTP server to serve the minimal frontend
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Set the directory to serve files from
PORT = 3000
DIRECTORY = Path(__file__).parent

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS support"""
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()

def main():
    """Start the HTTP server"""
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"🌐 Frontend server starting...")
        print(f"📍 Serving directory: {DIRECTORY}")
        print(f"🔗 Frontend URL: http://localhost:{PORT}")
        print(f"🔗 Backend API: http://localhost:8001")
        print(f"📖 API Docs: http://localhost:8001/docs")
        print(f"\n✅ Server ready! Open http://localhost:{PORT} in your browser")
        print(f"🛑 Press Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")
            sys.exit(0)

if __name__ == "__main__":
    main()
