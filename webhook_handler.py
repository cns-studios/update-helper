from flask import Flask, request, jsonify
import subprocess
import threading
import time
import requests

app = Flask(__name__)

def run_update(target, discord_webhook):
    """Execute the update and send logs to Discord"""
    try:
        if target == 'all':
            cmd = ['bash', 'hello_world.sh']
        elif target == 'project':
            cmd = ['bash', '/path/to/update_project.sh']
        elif target == 'group':
            cmd = ['bash', '/path/to/update_group.sh']
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        logs = f"**Update Complete: {target}**\n```\n"
        logs += result.stdout
        if result.stderr:
            logs += f"\nErrors:\n{result.stderr}"
        logs += "\n```"
        
        if len(logs) > 1990:
            logs = logs[:1990] + "...\n```\n(truncated)"
        
        requests.post(discord_webhook, json={"content": logs})
        
    except subprocess.TimeoutExpired:
        requests.post(discord_webhook, json={"content": f"Update for {target} timed out"})
    except Exception as e:
        requests.post(discord_webhook, json={"content": f"Error during update: {str(e)}"})

@app.route('/webhook/update', methods=['POST'])
def webhook_update():
    data = request.json
    target = data.get('target')
    delay = data.get('delay', 0)
    discord_webhook = data.get('discord_webhook')
    
    if delay > 0:
        def delayed_update():
            time.sleep(delay * 3600)
            run_update(target, discord_webhook)
        
        thread = threading.Thread(target=delayed_update)
        thread.daemon = True
        thread.start()
    else:
        thread = threading.Thread(target=run_update, args=(target, discord_webhook))
        thread.daemon = True
        thread.start()
    
    return jsonify({"status": "accepted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
