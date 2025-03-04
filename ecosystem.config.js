module.exports = {
  apps: [
    {
      name: "nijiapi",
      script: "bash",
      args: [
        "-c",
        "env/bin/uvicorn app.main:app --host 0.0.0.0 --port 7000 --workers 4"
      ],
      interpreter: "none",
      cwd: "/home/ubuntu/Niji-API",
      exec_mode: "fork",
      instances: 1,
      max_memory_restart: "4G",
      watch: false,
    },
    {
      name: "redis",
      script: "redis-server",
      interpreter: "none",
    }
  ],
};
