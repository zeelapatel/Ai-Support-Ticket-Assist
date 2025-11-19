import React, { useState, useEffect, useRef } from 'react';
import './ResizableSplitter.css';

function ResizableSplitter({ leftPanel, rightPanel, initialLeftWidth = '50%', minLeftWidth = 300, minRightWidth = 300 }) {
  const [leftWidth, setLeftWidth] = useState(initialLeftWidth);
  const [isResizing, setIsResizing] = useState(false);
  const containerRef = useRef(null);
  const leftPanelRef = useRef(null);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing || !containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      const newLeftWidth = e.clientX - containerRect.left;
      const containerWidth = containerRect.width;
      
      // Calculate percentages
      const leftPercent = (newLeftWidth / containerWidth) * 100;
      const rightPercent = 100 - leftPercent;

      // Check minimum widths
      const leftMinPercent = (minLeftWidth / containerWidth) * 100;
      const rightMinPercent = (minRightWidth / containerWidth) * 100;

      if (leftPercent >= leftMinPercent && rightPercent >= rightMinPercent) {
        setLeftWidth(`${leftPercent}%`);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, minLeftWidth, minRightWidth]);

  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsResizing(true);
  };

  return (
    <div className="resizable-container" ref={containerRef}>
      <div 
        className="resizable-left-panel" 
        ref={leftPanelRef}
        style={{ flexBasis: leftWidth, width: leftWidth }}
      >
        {leftPanel}
      </div>
      <div 
        className="resizable-splitter"
        onMouseDown={handleMouseDown}
      >
        <div className="splitter-handle"></div>
      </div>
      <div 
        className="resizable-right-panel"
        style={{ flex: '1 1 0%' }}
      >
        {rightPanel}
      </div>
    </div>
  );
}

export default ResizableSplitter;

