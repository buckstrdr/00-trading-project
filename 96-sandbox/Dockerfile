# Node.js base image
FROM node:20-alpine

# Install git and other dependencies
RUN apk add --no-cache git bash curl python3 make g++

# Create working directory
WORKDIR /project

# Install Claude Code globally
RUN npm install -g @anthropic-ai/claude-code

# Copy project files
COPY . /project/

# Set up git config (for safety)
RUN git config --global user.email "sandbox@local" && \
    git config --global user.name "Sandbox User"

# Create startup script
RUN echo '#!/bin/bash\n\
echo "========================================"\n\
echo "Claude Code YOLO Mode - Docker Container"\n\
echo "========================================"\n\
echo ""\n\
echo "Starting in YOLO mode (no permission prompts)..."\n\
echo ""\n\
claude --dangerously-skip-permissions' > /start-claude.sh && \
chmod +x /start-claude.sh

# Expose port if needed for any web services
EXPOSE 3000 8080

# Start Claude Code in YOLO mode
CMD ["/start-claude.sh"]