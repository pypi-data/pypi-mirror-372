---
layout: home

hero:
  name: "libfrankapy"
  text: "Python library for controlling Franka Emika robots"
  tagline: "High-performance Python bindings for libfranka with real-time control capabilities"
  actions:
    - theme: brand
      text: Get Started
      link: /installation
    - theme: alt
      text: View on GitHub
      link: https://github.com/han-xudong/libfrankapy

features:
  - icon: ⚡
    title: Real-time Performance
    details: C++ control loop maintains 1kHz real-time performance, Python does not participate in real-time loops
  - icon: 🐍
    title: Python Friendly
    details: Provides intuitive Python API with complete type hints
  - icon: 🚀
    title: Efficient Communication
    details: Uses shared memory and atomic operations for Python-C++ data exchange
  - icon: 🛡️
    title: Safety Control
    details: Complete safety limits, error handling, and emergency stop functionality
  - icon: 🎯
    title: Multiple Control Modes
    details: Supports joint space, Cartesian space, and trajectory control
  - icon: 📊
    title: Real-time Monitoring
    details: Complete robot state feedback and monitoring functionality
---
