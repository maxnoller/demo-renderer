# Use the official Ubuntu base image
FROM ubuntu:22.04

# Install sudo and necessary packages
RUN apt-get update \
    && apt-get install -y sudo

# Create the steam user and add to sudoers
RUN useradd -ms /bin/bash steam \
    && echo "steam ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

ENV DEBIAN_FRONTEND=noninteractive

USER root
# Install necessary packages
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      xvfb \
      x11-apps \
      wget \
      software-properties-common \
      libgl1-mesa-dri \
      libcurl4 \
      libudev1 \
      ca-certificates \
      dbus \
      libnvidia-gl-535 \
      vulkan-tools \
      mesa-vulkan-drivers \
      dbus-x11 \
      pciutils \
      ffmpeg \
      x11vnc \
      supervisor \
    && apt-get clean 

# Install Steam
RUN dpkg --add-architecture i386 \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      steam-installer \
    && apt-get clean

RUN mkdir -p /opt/steamcmd &&\
    cd /opt/steamcmd &&\
    curl -s https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz | tar -vxz &&\
    chown -R steam /opt/steamcmd

RUN apt-get remove -y xdg-desktop-portal \
    && apt-get clean

COPY ./scripts /home/steam/scripts
RUN chmod +x /home/steam/scripts/*

# Set default environment variables
ENV DISPLAY=:99
ENV XDG_RUNTIME_DIR="/tmp/.X11-unix/run"

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /home/steam/cs2/ && \
    chown -R steam:steam /home/steam/cs2/ && \
    chmod -R 755 /home/steam/cs2/

WORKDIR /home/steam
# Command to start Steam
CMD ["./scripts/entrypoint.sh"]
