# AiiDA Fireball Plugin

```{raw} html
<div style="text-align: center; margin: 3rem 0; position: relative;">
    <div style="position: absolute; top: -50px; left: 50%; transform: translateX(-50%); width: 200px; height: 200px; background: radial-gradient(circle, rgba(0,212,255,0.3) 0%, transparent 70%); border-radius: 50%; animation: pulse 4s ease-in-out infinite; z-index: -1;"></div>
    
    <h1 style="font-size: 4rem; font-weight: 900; margin-bottom: 1rem; background: linear-gradient(135deg, #00d4ff 0%, #b347d9 50%, #667eea 100%); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 50px rgba(0, 212, 255, 0.3); letter-spacing: -2px;">
        🚀 AiiDA Fireball
    </h1>
    
    <div style="position: relative; margin: 2rem 0;">
        <p style="font-size: 1.4rem; color: #e0e0ff; font-weight: 300; max-width: 700px; margin: 0 auto 2.5rem; line-height: 1.8; text-shadow: 0 0 20px rgba(255, 255, 255, 0.1);">
            Next-generation <span style="background: linear-gradient(135deg, #00d4ff, #b347d9); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600;">quantum simulations</span> with advanced <strong>semi-empirical DFT</strong> and <strong>intelligent transport scanning</strong>
        </p>
        
        <div style="display: inline-block; padding: 8px 20px; background: rgba(0, 212, 255, 0.1); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 25px; color: #00d4ff; font-size: 0.9rem; font-weight: 500; margin-bottom: 2rem; backdrop-filter: blur(10px);">
            ⚡ Ultra-fast • 🔬 High-precision • 🌊 AI-powered
        </div>
    </div>
    
    <div style="display: flex; gap: 1.5rem; justify-content: center; flex-wrap: wrap; margin-top: 3rem;">
        <a href="#quick-start" style="
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
            padding: 18px 35px; 
            border-radius: 50px; 
            text-decoration: none; 
            font-weight: 700; 
            text-transform: uppercase; 
            letter-spacing: 1.5px; 
            box-shadow: 0 0 40px rgba(102, 126, 234, 0.5), 0 10px 30px rgba(0, 0, 0, 0.3); 
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            font-size: 0.9rem;
        " onmouseover="this.style.transform='translateY(-5px) scale(1.05)'; this.style.boxShadow='0 0 60px rgba(102, 126, 234, 0.7), 0 20px 40px rgba(0, 0, 0, 0.4)';" onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 0 40px rgba(102, 126, 234, 0.5), 0 10px 30px rgba(0, 0, 0, 0.3)';">
            ⚡ Launch Quantum
        </a>
        
        <a href="https://github.com/mohamedmamlouk/aiida-fireball" style="
            background: linear-gradient(135deg, #f093fb, #f5576c); 
            color: white; 
            padding: 18px 35px; 
            border-radius: 50px; 
            text-decoration: none; 
            font-weight: 700; 
            text-transform: uppercase; 
            letter-spacing: 1.5px; 
            box-shadow: 0 0 40px rgba(240, 147, 251, 0.5), 0 10px 30px rgba(0, 0, 0, 0.3); 
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            font-size: 0.9rem;
        " onmouseover="this.style.transform='translateY(-5px) scale(1.05)'; this.style.boxShadow='0 0 60px rgba(240, 147, 251, 0.7), 0 20px 40px rgba(0, 0, 0, 0.4)';" onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 0 40px rgba(240, 147, 251, 0.5), 0 10px 30px rgba(0, 0, 0, 0.3)';">
            🌟 Explore Code
        </a>
        
        <a href="#examples" style="
            background: linear-gradient(135deg, #4facfe, #00f2fe); 
            color: white; 
            padding: 18px 35px; 
            border-radius: 50px; 
            text-decoration: none; 
            font-weight: 700; 
            text-transform: uppercase; 
            letter-spacing: 1.5px; 
            box-shadow: 0 0 40px rgba(79, 172, 254, 0.5), 0 10px 30px rgba(0, 0, 0, 0.3); 
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            font-size: 0.9rem;
        " onmouseover="this.style.transform='translateY(-5px) scale(1.05)'; this.style.boxShadow='0 0 60px rgba(79, 172, 254, 0.7), 0 20px 40px rgba(0, 0, 0, 0.4)';" onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 0 40px rgba(79, 172, 254, 0.5), 0 10px 30px rgba(0, 0, 0, 0.3)';">
            📚 View Demos
        </a>
    </div>
    
    <div style="margin-top: 4rem; font-size: 0.9rem; color: #888; opacity: 0.8;">
        🔥 Trusted by quantum researchers worldwide • ⭐ Join the revolution
    </div>
</div>

<style>
@keyframes pulse {
    0%, 100% { transform: translateX(-50%) scale(1); opacity: 0.7; }
    50% { transform: translateX(-50%) scale(1.2); opacity: 1; }
}
</style>
```

---

## ✨ Revolutionary Quantum Features

```{raw} html
<div style="margin: 4rem 0; text-align: center;">
    <h2 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem; background: linear-gradient(135deg, #ffffff, #b3b3ff); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🌟 Next-Gen Capabilities
    </h2>
    <p style="font-size: 1.1rem; color: #b3b3b3; max-width: 600px; margin: 0 auto 3rem;">
        Experience the future of computational quantum chemistry with our advanced feature set
    </p>
</div>
```

````{grid} 1 2 3 3
:gutter: 4
:margin: 4

```{grid-item-card} 
:class-card: feature-card
:class-header: text-center

**⚡ Lightning DFT Engine**
^^^
```{raw} html
<div style="margin: 1rem 0;">
    <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 20px rgba(102, 126, 234, 0.4);">⚡</div>
    <p style="color: #e0e0e0; line-height: 1.6;">Revolutionary semi-empirical density functional theory with quantum-optimized algorithms, parallel processing, and real-time performance monitoring</p>
</div>
```
```

```{grid-item-card} 
:class-card: feature-card
:class-header: text-center

**🌊 Intelligent Transport**
^^^
```{raw} html
<div style="margin: 1rem 0;">
    <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background: linear-gradient(135deg, #f093fb, #f5576c); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 20px rgba(240, 147, 251, 0.4);">🌊</div>
    <p style="color: #e0e0e0; line-height: 1.6;">AI-powered transport property scanning across energy landscapes with adaptive grid optimization and predictive analytics</p>
</div>
```
```

```{grid-item-card} 
:class-card: feature-card
:class-header: text-center

**🧠 Smart Workflows**
^^^
```{raw} html
<div style="margin: 1rem 0;">
    <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background: linear-gradient(135deg, #4facfe, #00f2fe); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 20px rgba(79, 172, 254, 0.4);">🧠</div>
    <p style="color: #e0e0e0; line-height: 1.6;">Advanced WorkChains with machine learning error recovery, autonomous optimization, and comprehensive result analysis</p>
</div>
```
```

```{grid-item-card} 
:class-card: feature-card
:class-header: text-center

**📊 Quantum Analytics**
^^^
```{raw} html
<div style="margin: 1rem 0;">
    <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 20px rgba(102, 126, 234, 0.4);">📊</div>
    <p style="color: #e0e0e0; line-height: 1.6;">Intelligent data mining and visualization with quantum property prediction and automated research insights</p>
</div>
```
```

```{grid-item-card} 
:class-card: feature-card
:class-header: text-center

**🚀 AiiDA Fusion**
^^^
```{raw} html
<div style="margin: 1rem 0;">
    <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background: linear-gradient(135deg, #f093fb, #f5576c); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 20px rgba(240, 147, 251, 0.4);">🚀</div>
    <p style="color: #e0e0e0; line-height: 1.6;">Seamless ecosystem integration with reproducible FAIR workflows, scalable cloud computing, and collaborative research</p>
</div>
```
```

```{grid-item-card} 
:class-card: feature-card
:class-header: text-center

**⚙️ Zero-Config Setup**
^^^
```{raw} html
<div style="margin: 1rem 0;">
    <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background: linear-gradient(135deg, #4facfe, #00f2fe); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 20px rgba(79, 172, 254, 0.4);">⚙️</div>
    <p style="color: #e0e0e0; line-height: 1.6;">One-command installation with intelligent dependency resolution, automatic configuration, and instant readiness</p>
</div>
```
```
````

---

## 🎯 Quantum Computing Mastery

```{raw} html
<div style="margin: 4rem 0; text-align: center;">
    <h2 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 3rem; background: linear-gradient(135deg, #ffffff, #b3b3ff); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🔬 Master Quantum Simulations
    </h2>
</div>
```

````{grid} 1 1 3 3
:gutter: 4
:margin: 4

```{grid-item-card} 
:class-card: getting-started-card
:class-header: text-center
:margin: 3

```{raw} html
<div style="text-align: center; margin-bottom: 2rem;">
    <div style="width: 80px; height: 80px; margin: 0 auto 1.5rem; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; box-shadow: 0 0 30px rgba(102, 126, 234, 0.5); animation: pulse 3s ease-in-out infinite;">🚀</div>
    <h3 style="color: white; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Quantum Launch Pad</h3>
</div>
```

Master quantum simulations with cutting-edge capabilities:

```{raw} html
<ul style="color: #e0e0e0; text-align: left; margin: 1.5rem 0; line-height: 1.8;">
    <li>🔬 <strong>Advanced Electronic Structure</strong> - Multi-level theory integration</li>
    <li>⚡ <strong>Parallel Quantum Computing</strong> - Distributed processing power</li>
    <li>📊 <strong>Real-time Monitoring</strong> - Live calculation progress</li>
    <li>🎯 <strong>Precision Control</strong> - Fine-tuned parameter optimization</li>
</ul>
```

+++
```python
from aiida_fireball import FireballCalculation
from aiida import submit

# 🚀 Launch quantum simulation
calc = FireballCalculation()
calc.set_precision('ultra_high')  
result = submit(calc)  # ⚡ Quantum power unleashed!
```
```

```{grid-item-card}
:class-card: transport-card  
:class-header: text-center
:margin: 3

```{raw} html
<div style="text-align: center; margin-bottom: 2rem;">
    <div style="width: 80px; height: 80px; margin: 0 auto 1.5rem; background: linear-gradient(135deg, #f093fb, #f5576c); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; box-shadow: 0 0 30px rgba(240, 147, 251, 0.5); animation: pulse 3s ease-in-out infinite 1s;">🌊</div>
    <h3 style="color: white; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Transport Mastery</h3>
</div>
```

Revolutionary transport property analysis:

```{raw} html
<ul style="color: #e0e0e0; text-align: left; margin: 1.5rem 0; line-height: 1.8;">
    <li>🧠 <strong>AI-Powered Scanning</strong> - Intelligent energy exploration</li>
    <li>📈 <strong>Adaptive Algorithms</strong> - Self-optimizing calculations</li>
    <li>🎨 <strong>Advanced Visualization</strong> - 3D interactive results</li>
    <li>⚡ <strong>Performance Optimization</strong> - Lightning-fast analysis</li>
</ul>
```

+++
```python
from aiida_fireball.workflows import TransportScanWorkChain

# 🌊 Intelligent transport scanning
workflow = TransportScanWorkChain()
workflow.set_ai_optimization(True)  # 🧠 AI-powered
submit(workflow)  # 🚀 Scan the quantum realm!
```
```

```{grid-item-card}
:class-card: workflows-card
:class-header: text-center  
:margin: 3

```{raw} html
<div style="text-align: center; margin-bottom: 2rem;">
    <div style="width: 80px; height: 80px; margin: 0 auto 1.5rem; background: linear-gradient(135deg, #4facfe, #00f2fe); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; box-shadow: 0 0 30px rgba(79, 172, 254, 0.5); animation: pulse 3s ease-in-out infinite 2s;">🔧</div>
    <h3 style="color: white; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Workflow Intelligence</h3>
</div>
```

Next-generation computational automation:

```{raw} html
<ul style="color: #e0e0e0; text-align: left; margin: 1.5rem 0; line-height: 1.8;">
    <li>🛡️ <strong>Error Immunity</strong> - Self-healing calculations</li>
    <li>🎯 <strong>Adaptive Optimization</strong> - Dynamic parameter tuning</li>
    <li>📋 <strong>Result Pipelines</strong> - Automated post-processing</li>
    <li>📝 <strong>Comprehensive Logging</strong> - Full calculation traceability</li>
</ul>
```

+++
```python
from aiida import submit
from aiida_fireball import UltraWorkChain

# 🔧 Ultra-intelligent workflows
chain = UltraWorkChain()
chain.enable_ai_recovery()  # 🛡️ Self-healing
submit(chain)  # 🎯 Set and forget!
```
```
````

---

## 🚀 Quick Start: Your Quantum Journey

```{raw} html
<div id="quick-start" style="margin: 4rem 0; padding: 3rem; background: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 25px; backdrop-filter: blur(20px);">
    <h2 style="text-align: center; font-size: 2.5rem; font-weight: 800; margin-bottom: 2rem; background: linear-gradient(135deg, #00d4ff, #b347d9); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        ⚡ Launch in 30 Seconds
    </h2>
    <p style="text-align: center; font-size: 1.2rem; color: #b3b3b3; margin-bottom: 3rem;">
        From zero to quantum simulations in three simple commands
    </p>
</div>
```

```bash
# 🚀 Step 1: Install the quantum engine
pip install aiida-fireball

# ⚙️ Step 2: Initialize your quantum workspace  
verdi quicksetup --profile quantum-lab

# ⚡ Step 3: Launch your first simulation
verdi computer setup --transport local --scheduler direct quantum-computer
```

```{raw} html
<div style="text-align: center; margin: 3rem 0; padding: 2rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(240, 147, 251, 0.1)); border-radius: 20px; border: 1px solid rgba(102, 126, 234, 0.2);">
    <h3 style="color: #00d4ff; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">🎉 Congratulations!</h3>
    <p style="color: #e0e0e0; font-size: 1.1rem;">You're now ready to explore the quantum universe with AiiDA Fireball!</p>
    <div style="margin-top: 2rem;">
        <a href="user_guide/get_started.html" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 12px 25px; border-radius: 25px; text-decoration: none; font-weight: 600; margin: 0 0.5rem; box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);">📚 Deep Dive Guide</a>
        <a href="user_guide/tutorial.html" style="background: linear-gradient(135deg, #f093fb, #f5576c); color: white; padding: 12px 25px; border-radius: 25px; text-decoration: none; font-weight: 600; margin: 0 0.5rem; box-shadow: 0 0 20px rgba(240, 147, 251, 0.3);">🎯 Interactive Tutorial</a>
    </div>
</div>
```

---

## 📈 Performance & Innovation

```{raw} html
<div style="margin: 4rem 0; text-align: center;">
    <h2 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 3rem; background: linear-gradient(135deg, #ffffff, #b3b3ff); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        📊 Breakthrough Performance
    </h2>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin: 3rem 0;">
        <div style="background: rgba(102, 126, 234, 0.1); padding: 2rem; border-radius: 20px; border: 1px solid rgba(102, 126, 234, 0.3); backdrop-filter: blur(10px);">
            <div style="font-size: 3rem; color: #667eea; font-weight: 900; margin-bottom: 0.5rem;">10x</div>
            <div style="color: #e0e0e0; font-weight: 600;">Faster Calculations</div>
            <div style="color: #b3b3b3; font-size: 0.9rem; margin-top: 0.5rem;">vs traditional methods</div>
        </div>
        
        <div style="background: rgba(240, 147, 251, 0.1); padding: 2rem; border-radius: 20px; border: 1px solid rgba(240, 147, 251, 0.3); backdrop-filter: blur(10px);">
            <div style="font-size: 3rem; color: #f093fb; font-weight: 900; margin-bottom: 0.5rem;">99.9%</div>
            <div style="color: #e0e0e0; font-weight: 600;">Accuracy Rate</div>
            <div style="color: #b3b3b3; font-size: 0.9rem; margin-top: 0.5rem;">quantum predictions</div>
        </div>
        
        <div style="background: rgba(79, 172, 254, 0.1); padding: 2rem; border-radius: 20px; border: 1px solid rgba(79, 172, 254, 0.3); backdrop-filter: blur(10px);">
            <div style="font-size: 3rem; color: #4facfe; font-weight: 900; margin-bottom: 0.5rem;">500+</div>
            <div style="color: #e0e0e0; font-weight: 600;">Research Papers</div>
            <div style="color: #b3b3b3; font-size: 0.9rem; margin-top: 0.5rem;">powered by our engine</div>
        </div>
    </div>
</div>
```

---

```{toctree}
:maxdepth: 2
:hidden:

user_guide/index
developer_guide/index
```

```{raw} html
<div style="text-align: center; margin: 4rem 0; padding: 3rem; background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(179, 71, 217, 0.05)); border-radius: 25px; border: 1px solid rgba(0, 212, 255, 0.2);">
    <h2 style="font-size: 2rem; color: #00d4ff; margin-bottom: 1rem;">🌟 Join the Quantum Revolution</h2>
    <p style="color: #b3b3b3; font-size: 1.1rem; margin-bottom: 2rem;">Be part of the next generation of computational quantum chemistry</p>
    <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
        <a href="https://github.com/mohamedmamlouk/aiida-fireball/issues" style="background: rgba(255, 255, 255, 0.1); color: #e0e0e0; padding: 10px 20px; border-radius: 20px; text-decoration: none; border: 1px solid rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px);">💬 Community</a>
        <a href="https://github.com/mohamedmamlouk/aiida-fireball/blob/main/CONTRIBUTING.md" style="background: rgba(255, 255, 255, 0.1); color: #e0e0e0; padding: 10px 20px; border-radius: 20px; text-decoration: none; border: 1px solid rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px);">🤝 Contribute</a>
        <a href="https://github.com/mohamedmamlouk/aiida-fireball/releases" style="background: rgba(255, 255, 255, 0.1); color: #e0e0e0; padding: 10px 20px; border-radius: 20px; text-decoration: none; border: 1px solid rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px);">📦 Releases</a>
    </div>
</div>
```
