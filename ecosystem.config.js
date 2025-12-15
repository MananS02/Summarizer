module.exports = {
    apps: [{
        name: 'pdf-learning-platform',
        script: './backend/server.js',
        instances: 1,
        exec_mode: 'fork',
        env: {
            NODE_ENV: 'development',
            PORT: 3000
        },
        env_production: {
            NODE_ENV: 'production',
            PORT: 3000
        },
        error_file: './logs/err.log',
        out_file: './logs/out.log',
        log_file: './logs/combined.log',
        time: true,
        max_memory_restart: '1G',
        autorestart: true,
        watch: false,
        ignore_watch: ['node_modules', 'logs', 'public/uploads'],
        max_restarts: 10,
        min_uptime: '10s'
    }]
};
