/**
 * 生成环形图SVG代码
 * @param {Array} data - 数据数组，格式: [{color: 'red', scale: 30}, ...]
 * @param {Array} radius - 半径数组，格式: [外环半径, 内环半径]
 * @returns {string} SVG代码
 */
export function generateDonutChartSVG(data, radius) {
  const [outerRadius, innerRadius] = radius;
  const size = outerRadius * 2;
  const centerX = outerRadius;
  const centerY = outerRadius;

  // 计算总scale
  const totalScale = data.reduce((sum, item) => sum + item.scale, 0);

  // 辅助函数：根据角度和半径计算坐标点
  function polarToCartesian(centerX, centerY, radius, angleInDegrees) {
    const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
    return {
      x: centerX + (radius * Math.cos(angleInRadians)),
      y: centerY + (radius * Math.sin(angleInRadians))
    };
  }

  // 生成环形扇区路径
  function createArcPath(startAngle, endAngle, outerR, innerR) {
    const outerStart = polarToCartesian(centerX, centerY, outerR, endAngle);
    const outerEnd = polarToCartesian(centerX, centerY, outerR, startAngle);
    const innerStart = polarToCartesian(centerX, centerY, innerR, endAngle);
    const innerEnd = polarToCartesian(centerX, centerY, innerR, startAngle);

    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

    const pathData = [
      `M ${outerStart.x} ${outerStart.y}`,
      `A ${outerR} ${outerR} 0 ${largeArcFlag} 0 ${outerEnd.x} ${outerEnd.y}`,
      `L ${innerEnd.x} ${innerEnd.y}`,
      `A ${innerR} ${innerR} 0 ${largeArcFlag} 1 ${innerStart.x} ${innerStart.y}`,
      'Z'
    ].join(' ');

    return pathData;
  }

  // 生成所有扇区
  let currentAngle = 0;
  const paths = data.map(item => {
    const angle = (item.scale / totalScale) * 360;
    const pathData = createArcPath(currentAngle, currentAngle + angle, outerRadius, innerRadius);
    const path = `<path d="${pathData}" fill="${item.color}" />`;
    currentAngle += angle;
    return path;
  }).join('\n  ');

  // 生成完整SVG
  const svg = `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">${paths}</svg>`;

  return svg;
}