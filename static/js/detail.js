function radar(radarData, domId = 'radar') {
    const radarChart = echarts.init(document.getElementById(domId));
    const indicators = Object.keys(radarData.scores).map(k => ({name: k, max: 10}));

    const option = {
        title: {text: '声誉 / 影响力 / 速度 评分', left: 'center'},
        tooltip: {},
        radar: {indicator: indicators},
        series: [{
            name: radarData.name,
            type: 'radar',
            data: [{
                value: Object.values(radarData.scores),
                name: radarData.name
            }]
        }]
    };

    radarChart.setOption(option);
}