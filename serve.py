#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سيرفر ويب محلي لموقع متجر نينجا العراق
Local web server for Iraq Ninja Store

الاستخدام / Usage:
    python serve.py
    
سيفتح السيرفر على: http://localhost:8000
The server will open at: http://localhost:8000
"""

import http.server
import socketserver
import webbrowser
import os
from functools import partial

PORT = 8000

class ArabicHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    HTTP Request Handler with proper UTF-8 encoding for Arabic content
    """
    
    def end_headers(self):
        # إضافة UTF-8 encoding للملفات
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        super().end_headers()
    
    def log_message(self, format, *args):
        """تسجيل الطلبات مع دعم اللغة العربية"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server():
    """تشغيل السيرفر المحلي"""
    
    # التأكد من أننا في المجلد الصحيح
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # إنشاء السيرفر
    Handler = ArabicHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("=" * 60)
        print("🚀 سيرفر متجر نينجا العراق يعمل الآن!")
        print("=" * 60)
        print(f"📍 العنوان المحلي: http://localhost:{PORT}")
        print(f"📁 المجلد: {script_dir}")
        print("=" * 60)
        print("💡 لإيقاف السيرفر اضغط: Ctrl+C")
        print("=" * 60)
        
        # فتح المتصفح تلقائياً
        webbrowser.open(f'http://localhost:{PORT}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n")
            print("=" * 60)
            print("⏹️  تم إيقاف السيرفر")
            print("=" * 60)


if __name__ == "__main__":
    run_server()
