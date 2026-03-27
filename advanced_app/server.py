import http.server
import socketserver
import urllib.parse
import subprocess
import os

PORT = 8080

class VulnerableHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # route1: home page
        if path == "/":
            self.serve_html("")

        # route2: ping
        elif path == "/ping":
          
            query = urllib.parse.parse_qs(parsed_path.query)
            ip_address = query.get("ip", [""])[0]

            
            command = f"ping -c 3 {ip_address}"
            
            try:
               
                output = subprocess.check_output(
                    command, 
                    shell=True, 
                    stderr=subprocess.STDOUT, 
                    text=True
                )
            except subprocess.CalledProcessError as e:
             
                output = e.output
            except Exception as e:
                output = str(e)


            result_html = f"<h3>executing： <code>{command}</code></h3><div class='terminal'><pre>{output}</pre></div>"
            
            self.serve_html(result_html)
        
        else:
            self.send_error(404, "Page Not Found")

    def serve_html(self, result_content):
       
        try:
            with open("public/index.html", "r", encoding="utf-8") as f:
                html_content = f.read()
            
      
            html_content = html_content.replace("", result_content)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))
        except FileNotFoundError:
            self.send_error(404, "cannot find public/index.html")

os.chdir(os.path.dirname(os.path.abspath(__file__)))


with socketserver.TCPServer(("", PORT), VulnerableHandler) as httpd:
    print("="*50)
    print(f"server activated")
    print(f"input http://localhost:{PORT}")
    print("Ctrl+C to shutdown")
    print("="*50)
    httpd.serve_forever()