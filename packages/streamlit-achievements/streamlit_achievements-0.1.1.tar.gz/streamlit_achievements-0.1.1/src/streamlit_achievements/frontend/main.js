// The `Streamlit` object exists because our html file includes
// `streamlit-component-lib.js`.
// If you get an error about "Streamlit" not being defined, that
// means you're missing that file.

// Track current achievement to prevent interruptions  
let lastAchievementTime = 0;
let currentAchievementId = null;

// Animation timing constants (ms)
const TIMINGS = {
  slideIn: 800,
  expandDelay: 800,         // when background starts expanding
  expandDuration: 2500,     // how long the background expands
  textTitleDelay: 1500,
  textDescriptionDelay: 1800,
  textPointsDelay: 2100,
  slideOut: 450,
  defaultDuration: 6500     // new default display duration
};
const FILL_COMPLETE = TIMINGS.expandDelay + TIMINGS.expandDuration; // 3300ms with current values
const WAIT_AFTER_FILL_MS = 3000; // wait 3s after fill before dissolving by default

function sendValue(value) {
  Streamlit.setComponentValue(value)
}

function createFloatingAchievementInParent(achievementData) {
  // Send message to parent window to create floating achievement
  const message = {
    type: 'STREAMLIT_ACHIEVEMENT_FLOATING',
    data: achievementData
  };
  
  console.log('Sending floating achievement to parent window:', message);
  window.parent.postMessage(message, '*');
}

function createAchievement(title, description, points, iconText, duration, iconBackgroundColor, backgroundColor, textColor, shadowColor, autoWidth, floating, position, dissolve, timestamp) {
  const container = document.getElementById('root');
  
  // Use timestamp as unique achievement ID
  const achievementId = `achievement_${timestamp}`;
  
  // Don't interrupt ongoing animations (minimum 1 second between achievements)
  if (timestamp - lastAchievementTime < 1000 && currentAchievementId) {
    console.log('Preventing interruption of ongoing achievement');
    return;
  }
  
  // Check if same achievement is already showing using timestamp
  if (currentAchievementId === achievementId) {
    console.log('Same achievement already showing, skipping');
    return;
  }
  
  // Update tracking variables  
  lastAchievementTime = timestamp;
  currentAchievementId = achievementId;
  
  console.log('Creating achievement:', { title, description, points, iconText, autoWidth, floating, position, achievementId });
  
  // Clear any existing achievements for inline mode
  if (!floating) {
    container.innerHTML = '';
  }
  
  // For floating achievements, try to escape iframe by creating in parent document
  if (floating) {
    try {
      // Try to create floating achievement in parent document
      const parentDoc = window.parent.document;
      createFloatingAchievement(parentDoc, achievementId, title, description, points, iconText, duration, iconBackgroundColor, backgroundColor, textColor, shadowColor, autoWidth, position, dissolve);
      
      // Set minimal frame height for floating
      Streamlit.setFrameHeight(1);
      
      // Send completion status back to Streamlit
      sendValue({
        status: 'shown',
        title: title,
        description: description,
        points: points,
        timestamp: timestamp,
        floating: true
      });
      return;
    } catch (e) {
      console.warn('Cannot access parent document for floating achievement, using fallback');
      // Fall back to regular achievement if parent access fails
    }
  }
  
  // Create regular achievement (or fallback for floating)
  createRegularAchievement(container, achievementId, title, description, points, iconText, duration, iconBackgroundColor, backgroundColor, textColor, shadowColor, autoWidth, floating, position, dissolve);
}

function createFloatingAchievement(doc, achievementId, title, description, points, iconText, duration, iconBackgroundColor, backgroundColor, textColor, shadowColor, autoWidth, position, dissolve) {
  // Create achievement element in parent document
  const achievementContainer = doc.createElement('div');
  achievementContainer.className = 'streamlit-floating-achievement';
  achievementContainer.setAttribute('data-achievement-id', achievementId);
  
  // Apply styles directly to ensure they work
  const styles = {
    position: 'fixed',
    zIndex: '10000',
    left: '50%',
    width: '400px',
    maxWidth: 'calc(100vw - 40px)',
    minWidth: '300px',
    height: '80px',
    margin: '0',
    transform: 'translateX(-50%) translateX(-100%)',
    opacity: '0',
    transition: 'all 0.8s ease-out',
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    pointerEvents: 'none'
  };
  
  // Position specific styles - support both predefined positions and pixel values
  if (position.endsWith('px')) {
    // Custom pixel position from top
    styles.top = position;
  } else {
    switch(position) {
      case 'middle':
        styles.top = '50%';
        styles.transform = 'translateX(-50%) translateY(-50%) translateX(-100%)';
        break;
      case 'bottom':
        styles.bottom = '20px';
        break;
      default: // 'top'
        styles.top = '20px';
    }
  }
  
  // Apply styles
  Object.assign(achievementContainer.style, styles);
  
  // Handle empty values
  const displayTitle = title || "";
  const displayDescription = description || "";
  const displayPoints = points || 0;
  const displayIcon = iconText || "";
  const shouldShowPoints = displayPoints > 0;
  
  // Create achievement content with inline styles to ensure rendering
  achievementContainer.innerHTML = `
    <div style="
      position: relative;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, ${iconBackgroundColor || '#8BC34A'} 0%, ${iconBackgroundColor || '#8BC34A'} 100%);
      border-radius: 40px;
      display: flex;
      align-items: center;
      padding: 0;
      overflow: hidden;
      box-shadow: 0 8px 32px ${shadowColor || 'rgba(0,0,0,0.3)'};
      border: 2px solid ${backgroundColor || '#2E7D32'};
    ">
      <div style="
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, ${backgroundColor || '#2E7D32'} 0%, ${backgroundColor || '#2E7D32'} 100%);
        border-radius: 38px;
        transform: scaleX(0);
        transform-origin: left center;
        animation: expandBackground 2.5s ease-out 0.8s forwards;
      "></div>
      <div style="
        position: relative;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, ${iconBackgroundColor || '#8BC34A'} 0%, ${iconBackgroundColor || '#8BC34A'} 100%);
        border-radius: 50%;
        margin: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        color: ${textColor || '#FFFFFF'};
        text-shadow: 0 1px 3px ${shadowColor || 'rgba(0,0,0,0.3)'};
        border: 3px solid ${backgroundColor || '#2E7D32'};
        z-index: 2;
        animation: iconPulse 0.8s ease-out 1.2s;
      ">${displayIcon}</div>
      <div style="
        position: relative;
        flex: 1;
        padding: 10px 20px 10px 0;
        z-index: 2;
        color: ${textColor || '#FFFFFF'};
      ">
        <div style="
          font-size: 14px;
          font-weight: 600;
          margin: 0 0 4px 0;
          text-shadow: 0 1px 2px ${shadowColor || 'rgba(0,0,0,0.3)'};
          opacity: 0;
          animation: fadeInText 0.6s ease-out 1.5s forwards;
          display: ${displayTitle ? 'block' : 'none'};
        ">${displayTitle}</div>
        <div style="
          font-size: 18px;
          font-weight: bold;
          margin: 0;
          text-shadow: 0 1px 2px ${shadowColor || 'rgba(0,0,0,0.3)'};
          opacity: 0;
          animation: fadeInText 0.6s ease-out 1.8s forwards;
          display: ${displayDescription ? 'block' : 'none'};
        ">${displayDescription}</div>
      </div>
      <div style="
        position: absolute;
        top: 50%;
        right: 20px;
        transform: translateY(-50%);
        background: rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 4px 12px;
        font-size: 12px;
        font-weight: bold;
        color: ${textColor || '#FFFFFF'};
        text-shadow: 0 1px 2px ${shadowColor || 'rgba(0,0,0,0.3)'};
        z-index: 2;
        opacity: 0;
        animation: fadeInText 0.6s ease-out 2.1s forwards;
        display: ${shouldShowPoints ? 'block' : 'none'};
      ">${displayPoints}P</div>
    </div>
  `;
  
  // Add required animations as style element
  if (!doc.getElementById('streamlit-achievement-animations')) {
    const styleElement = doc.createElement('style');
    styleElement.id = 'streamlit-achievement-animations';
    styleElement.textContent = `
      @keyframes expandBackground {
        0% { transform: scaleX(0); }
        100% { transform: scaleX(1); }
      }
      @keyframes iconPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.15); }
      }
      @keyframes fadeInText {
        to { opacity: 1; }
      }
    `;
    doc.head.appendChild(styleElement);
  }
  
  // Add to parent document
  doc.body.appendChild(achievementContainer);
  
  // Trigger slide-in animation
  setTimeout(() => {
    achievementContainer.style.opacity = '1';
    if (position === 'middle') {
      achievementContainer.style.transform = 'translateX(-50%) translateY(-50%)';
    } else if (position.endsWith('px')) {
      achievementContainer.style.transform = 'translateX(-50%)';
    } else {
      achievementContainer.style.transform = 'translateX(-50%)';
    }
  }, 50);
  
  // Compute dissolve and duration to ensure background fully fills first
  const effectiveDuration = Math.max(duration || TIMINGS.defaultDuration, FILL_COMPLETE + TIMINGS.slideOut + 1000);
  // Determine when to dissolve: default is 2s after background is filled
  let effectiveDissolve;
  if (typeof dissolve === 'number' && dissolve > 0) {
    effectiveDissolve = Math.max(dissolve, FILL_COMPLETE + WAIT_AFTER_FILL_MS);
  } else {
    effectiveDissolve = FILL_COMPLETE + WAIT_AFTER_FILL_MS;
  }
  // Ensure dissolve happens before auto-hide
  effectiveDissolve = Math.min(effectiveDissolve, Math.max(0, effectiveDuration - TIMINGS.slideOut - 50));

  let earlyHidden = false;
  // Start disappearing at dissolve time: fade + slide-out together, faster
  setTimeout(() => {
    earlyHidden = true;
    achievementContainer.style.transition = `opacity ${TIMINGS.slideOut}ms ease-out, transform ${TIMINGS.slideOut}ms ease-in`;
    achievementContainer.style.opacity = '0';
    if (position === 'middle') {
      achievementContainer.style.transform = 'translateX(-50%) translateY(-50%) translateX(100%)';
    } else {
      achievementContainer.style.transform = 'translateX(-50%) translateX(100%)';
    }
    const cleanup = () => {
      if (doc.body.contains(achievementContainer)) doc.body.removeChild(achievementContainer);
      if (currentAchievementId === achievementId) currentAchievementId = null;
    };
    const onEnd = () => {
      achievementContainer.removeEventListener('transitionend', onEnd);
      cleanup();
    };
    achievementContainer.addEventListener('transitionend', onEnd);
    setTimeout(cleanup, TIMINGS.slideOut + 200);
  }, effectiveDissolve);
  
  // Auto-hide after duration
  const minDuration = effectiveDuration;
  const cleanup = () => {
    if (doc.body.contains(achievementContainer)) {
      doc.body.removeChild(achievementContainer);
    }
    if (currentAchievementId === achievementId) {
      currentAchievementId = null;
    }
  };

  setTimeout(() => {
    if (earlyHidden) return; // already handled by early dissolve
    achievementContainer.style.transition = 'all 0.8s ease-in';
    achievementContainer.style.opacity = '0';
    if (position === 'middle') {
      achievementContainer.style.transform = 'translateX(-50%) translateY(-50%) translateX(100%)';
    } else {
      achievementContainer.style.transform = 'translateX(-50%) translateX(100%)';
    }
    // Prefer transitionend for robust cleanup, with timeout fallback
    const onEnd = () => {
      achievementContainer.removeEventListener('transitionend', onEnd);
      cleanup();
    };
    achievementContainer.addEventListener('transitionend', onEnd);
    setTimeout(cleanup, TIMINGS.slideOut + 200);
  }, minDuration);
}

function createRegularAchievement(container, achievementId, title, description, points, iconText, duration, iconBackgroundColor, backgroundColor, textColor, shadowColor, autoWidth, floating, position, dissolve) {
  // Create the achievement element
  const achievementContainer = document.createElement('div');
  achievementContainer.className = 'achievement-container';
  achievementContainer.setAttribute('data-achievement-id', achievementId);
  
  // Add CSS classes based on configuration
  if (autoWidth) {
    achievementContainer.classList.add('auto-width');
  }
  
  // Set custom colors using CSS custom properties with fallbacks
  achievementContainer.style.setProperty('--light-green', iconBackgroundColor || '#8BC34A');
  achievementContainer.style.setProperty('--dark-green', backgroundColor || '#2E7D32');
  achievementContainer.style.setProperty('--text-color', textColor || '#FFFFFF');
  achievementContainer.style.setProperty('--shadow-color', shadowColor || 'rgba(0,0,0,0.3)');
  
  // Handle empty values - show defaults or hide elements
  const displayTitle = title || "";
  const displayDescription = description || "";
  const displayPoints = points || 0;
  const displayIcon = iconText || "";
  
  // Check if points should be displayed (not 0, not empty string, not null/undefined)
  const shouldShowPoints = displayPoints > 0 && displayPoints !== "" && displayPoints !== null;
  
  achievementContainer.innerHTML = `
    <div class="achievement-notification">
      <div class="achievement-background"></div>
      <div class="achievement-icon">${displayIcon}</div>
      <div class="achievement-content">
        <div class="achievement-title" style="display: ${displayTitle ? 'block' : 'none'}">${displayTitle}</div>
        <div class="achievement-description" style="display: ${displayDescription ? 'block' : 'none'}">${displayDescription}</div>
      </div>
      <div class="achievement-points" style="display: ${shouldShowPoints ? 'block' : 'none'}">${displayPoints}P</div>
    </div>
  `;
  
  container.appendChild(achievementContainer);
  
  // Set appropriate frame height
  Streamlit.setFrameHeight(120);
  
  // Compute dissolve and duration to ensure background fully fills first
  const effectiveDuration = Math.max(duration || TIMINGS.defaultDuration, FILL_COMPLETE + TIMINGS.slideOut + 1000);
  // Determine when to dissolve: default is 2s after background is filled
  let effectiveDissolve;
  if (typeof dissolve === 'number' && dissolve > 0) {
    effectiveDissolve = Math.max(dissolve, FILL_COMPLETE + WAIT_AFTER_FILL_MS);
  } else {
    effectiveDissolve = FILL_COMPLETE + WAIT_AFTER_FILL_MS;
  }
  effectiveDissolve = Math.min(effectiveDissolve, Math.max(0, effectiveDuration - TIMINGS.slideOut - 50));

  let earlyHidden = false;
  setTimeout(() => {
    const element = container.querySelector(`[data-achievement-id="${achievementId}"]`);
    if (!element) return;
    earlyHidden = true;
    // Start slide-out animation (opacity to 0 and slide) immediately
    element.classList.add('slide-out');
    const cleanup = () => {
      if (container.contains(element)) {
        container.removeChild(element);
        console.log('Achievement removed (early dissolve):', achievementId);
      }
      if (currentAchievementId === achievementId) currentAchievementId = null;
    };
    const onAnimEnd = () => {
      element.removeEventListener('animationend', onAnimEnd);
      cleanup();
    };
    element.addEventListener('animationend', onAnimEnd);
    setTimeout(cleanup, TIMINGS.slideOut + 200);
  }, effectiveDissolve);
  
  // Auto-hide after specified duration
  const minDuration = effectiveDuration;
  const hideTimeout = setTimeout(() => {
    const element = container.querySelector(`[data-achievement-id="${achievementId}"]`);
    if (earlyHidden || !element) return; // already handled
    if (element && !element.classList.contains('slide-out')) {
      console.log('Starting slide-out for achievement:', achievementId);
      element.classList.add('slide-out');
      const cleanup = () => {
        if (container.contains(element)) {
          container.removeChild(element);
          console.log('Achievement removed:', achievementId);
        }
        if (currentAchievementId === achievementId) {
          currentAchievementId = null;
        }
      };
      // Prefer animationend to ensure cleanup, with timeout fallback
      const onAnimEnd = () => {
        element.removeEventListener('animationend', onAnimEnd);
        cleanup();
      };
      element.addEventListener('animationend', onAnimEnd);
      setTimeout(cleanup, TIMINGS.slideOut + 200);
    }
  }, minDuration);
  
  // Store timeout ID on element for potential cleanup
  achievementContainer.setAttribute('data-timeout-id', hideTimeout);
  
  // Send completion status back to Streamlit
  sendValue({
    status: 'shown',
    title: title,
    description: description,
    points: points,
    timestamp: Date.now(),
    floating: floating
  });
}

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
function onRender(event) {
  // Get the data passed from Python
  const {
    title, 
    description, 
    points, 
    icon_text, 
    duration,
    icon_background_color,
    background_color, 
    text_color,
    shadow_color,
    auto_width,
    floating,
    position,
    dissolve,
    timestamp
  } = event.detail.args;
  
  // Skip if no arguments are provided (initial render)
  if (!event.detail.args || timestamp === undefined) {
    return;
  }
  
  console.log('onRender called with:', { title, description, points, icon_text, auto_width, floating, position, timestamp });
  
  // Only create achievement if we have been called with valid parameters
  // This includes empty achievement tests
  createAchievement(
    title, 
    description, 
    points, 
    icon_text, 
    duration || TIMINGS.defaultDuration,
    icon_background_color || "#8BC34A",
    background_color || "#2E7D32", 
    text_color || "#FFFFFF",
    shadow_color || "rgba(0,0,0,0.3)",
    auto_width !== false, // Default to true
    floating || false,
    position || "top",
    dissolve || 0,
    timestamp
  );
}

// Render the component whenever python send a "render event"
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
// Tell Streamlit that the component is ready to receive events
Streamlit.setComponentReady()
// Render with the correct height - will be updated dynamically based on floating mode
Streamlit.setFrameHeight(120)

// Inject floating achievement handler into parent window
function injectParentWindowHandler() {
  if (window.parent && window.parent !== window) {
    try {
      // Check if handler already exists
      if (window.parent.streamlitAchievementHandlerInjected) {
        return;
      }
      
      const scriptContent = `
        // Mark as injected
        window.streamlitAchievementHandlerInjected = true;
        
        // CSS for floating achievements in parent window
        const achievementCSS = \`
          .streamlit-floating-achievement {
            position: fixed;
            z-index: 999999;
            left: 50%;
            margin: 0;
            opacity: 0;
            transform: translateX(-50%) translateX(-100%);
            width: 400px;
            max-width: calc(100vw - 40px);
            min-width: 300px;
            height: 80px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            pointer-events: none;
          }
          
          .streamlit-floating-achievement.auto-width {
            width: calc(100vw - 40px);
            max-width: 600px;
          }
          
          .streamlit-floating-achievement.top {
            top: 20px;
          }
          
          .streamlit-floating-achievement.middle {
            top: 50%;
            transform: translateX(-50%) translateY(-50%) translateX(-100%);
          }
          
          .streamlit-floating-achievement.bottom {
            bottom: 20px;
          }
          
          .streamlit-floating-achievement .achievement-notification {
            position: relative;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, var(--light-green) 0%, var(--light-green) 100%);
            border-radius: 40px;
            display: flex;
            align-items: center;
            padding: 0;
            overflow: hidden;
            box-shadow: 0 4px 20px var(--shadow-color);
            border: 2px solid var(--dark-green);
          }
          
          .streamlit-floating-achievement .achievement-background {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, var(--dark-green) 0%, var(--dark-green) 100%);
            border-radius: 38px;
            transform: scaleX(0);
            transform-origin: left center;
            animation: streamlit-expandBackground 2.5s ease-out 0.8s forwards;
          }
          
          @keyframes streamlit-expandBackground {
            0% { transform: scaleX(0); }
            100% { transform: scaleX(1); }
          }
          
          .streamlit-floating-achievement .achievement-icon {
            position: relative;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, var(--light-green) 0%, var(--light-green) 100%);
            border-radius: 50%;
            margin: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            color: var(--text-color);
            text-shadow: 0 1px 3px var(--shadow-color);
            border: 3px solid var(--dark-green);
            z-index: 2;
            animation: streamlit-iconPulse 0.8s ease-out 1.2s;
          }
          
          @keyframes streamlit-iconPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.15); }
          }
          
          .streamlit-floating-achievement .achievement-content {
            position: relative;
            flex: 1;
            padding: 10px 20px 10px 0;
            z-index: 2;
            color: var(--text-color);
          }
          
          .streamlit-floating-achievement .achievement-title {
            font-size: 14px;
            font-weight: 600;
            margin: 0 0 4px 0;
            text-shadow: 0 1px 2px var(--shadow-color);
            opacity: 0;
            animation: streamlit-fadeInText 0.6s ease-out 1.5s forwards;
          }
          
          .streamlit-floating-achievement .achievement-description {
            font-size: 18px;
            font-weight: bold;
            margin: 0;
            text-shadow: 0 1px 2px var(--shadow-color);
            opacity: 0;
            animation: streamlit-fadeInText 0.6s ease-out 1.8s forwards;
          }
          
          .streamlit-floating-achievement .achievement-points {
            position: absolute;
            top: 50%;
            right: 20px;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: bold;
            color: var(--text-color);
            text-shadow: 0 1px 2px var(--shadow-color);
            z-index: 2;
            opacity: 0;
            animation: streamlit-fadeInText 0.6s ease-out 2.1s forwards;
          }
          
          @keyframes streamlit-fadeInText {
            to { opacity: 1; }
          }
          
          .streamlit-floating-achievement.slide-in {
            animation: streamlit-slideInFloating 0.8s ease-out forwards;
          }
          
          .streamlit-floating-achievement.middle.slide-in {
            animation: streamlit-slideInMiddle 0.8s ease-out forwards;
          }
          
          @keyframes streamlit-slideInFloating {
            from {
              opacity: 0;
              transform: translateX(-50%) translateX(-100%);
            }
            to {
              opacity: 1;
              transform: translateX(-50%) translateX(0);
            }
          }
          
          @keyframes streamlit-slideInMiddle {
            from {
              opacity: 0;
              transform: translateX(-50%) translateY(-50%) translateX(-100%);
            }
            to {
              opacity: 1;
              transform: translateX(-50%) translateY(-50%) translateX(0);
            }
          }
          
          .streamlit-floating-achievement.slide-out {
            animation: streamlit-slideOutFloating 0.45s ease-in forwards;
          }
          
          .streamlit-floating-achievement.middle.slide-out {
            animation: streamlit-slideOutMiddle 0.45s ease-in forwards;
          }
          
          @keyframes streamlit-slideOutFloating {
            to {
              opacity: 0;
              transform: translateX(-50%) translateX(100%);
            }
          }
          
          @keyframes streamlit-slideOutMiddle {
            to {
              opacity: 0;
              transform: translateX(-50%) translateY(-50%) translateX(100%);
            }
          }
        \`;
        
        // Inject CSS into parent document
        if (!document.getElementById('streamlit-achievement-styles')) {
          const styleElement = document.createElement('style');
          styleElement.id = 'streamlit-achievement-styles';
          styleElement.textContent = achievementCSS;
          document.head.appendChild(styleElement);
        }
        
        // Message handler for floating achievements
        function handleAchievementMessage(event) {
          if (event.data && event.data.type === 'STREAMLIT_ACHIEVEMENT_FLOATING') {
            const data = event.data.data;
            console.log('Received floating achievement data in parent:', data);
            createFloatingAchievementInParent(data);
          }
        }
        
        function createFloatingAchievementInParent(data) {
          // Remove any existing achievements
          const existing = document.querySelectorAll('.streamlit-floating-achievement');
          existing.forEach(el => el.remove());
          
          // Create achievement element
          const achievement = document.createElement('div');
          achievement.className = 'streamlit-floating-achievement';
          achievement.setAttribute('data-achievement-id', data.achievementId);
          
          // Add position class
          achievement.classList.add(data.position || 'top');
          
          // Add auto-width class if needed
          if (data.autoWidth) {
            achievement.classList.add('auto-width');
          }
          
          // Set CSS custom properties for colors
          achievement.style.setProperty('--light-green', data.iconBackgroundColor);
          achievement.style.setProperty('--dark-green', data.backgroundColor);
          achievement.style.setProperty('--text-color', data.textColor);
          achievement.style.setProperty('--shadow-color', data.shadowColor);
          
          // Check if points should be displayed
          const shouldShowPoints = data.points > 0 && data.points !== "" && data.points !== null;
          
          achievement.innerHTML = \`
            <div class="achievement-notification">
              <div class="achievement-background"></div>
              <div class="achievement-icon">\${data.iconText}</div>
              <div class="achievement-content">
                <div class="achievement-title" style="display: \${data.title ? 'block' : 'none'}">\${data.title}</div>
                <div class="achievement-description" style="display: \${data.description ? 'block' : 'none'}">\${data.description}</div>
              </div>
              <div class="achievement-points" style="display: \${shouldShowPoints ? 'block' : 'none'}">\${data.points}P</div>
            </div>
          \`;
          
          // Add to document
          document.body.appendChild(achievement);
          
          // Trigger slide-in animation
          setTimeout(() => {
            achievement.classList.add('slide-in');
          }, 50);
          
          // Auto-hide after duration
          setTimeout(() => {
            if (document.body.contains(achievement)) {
              achievement.classList.add('slide-out');
              setTimeout(() => {
                if (document.body.contains(achievement)) {
                  document.body.removeChild(achievement);
                }
              }, 500);
            }
          }, data.duration);
        }
        
        // Add event listener if not already added
        if (!window.streamlitAchievementListenerAdded) {
          window.addEventListener('message', handleAchievementMessage);
          window.streamlitAchievementListenerAdded = true;
          console.log('Streamlit floating achievement handler injected into parent window');
        }
      `;
      
      // Create and inject script
      const script = window.parent.document.createElement('script');
      script.textContent = scriptContent;
      window.parent.document.head.appendChild(script);
      
    } catch (error) {
      console.log('Could not inject parent window handler (cross-origin):', error);
    }
  }
}

// Try to inject the handler when component loads
try {
  injectParentWindowHandler();
} catch (error) {
  console.log('Initial injection failed:', error);
}
