module.exports = {
  apps: [{
    name: "pulsebnb-croo-agent",
    script: "croo_provider.py",
    interpreter: "/home/vps/pulsebnb-croo/venv/bin/python3",
    cwd: "/home/vps/pulsebnb-croo",
    env_file: ".env",
    autorestart: true,
    max_restarts: 10,
    restart_delay: 5000,
  }]
}
