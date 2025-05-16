function parseNumeric(arr) {
    return arr.map(v => {
        const num = parseFloat(v);
        return isNaN(num) ? 0 : num;
    });
}


function factor(factorData, domId = 'factor') {
    const chartDom = document.getElementById(domId);
    const myChart = echarts.init(chartDom);

    const upperLimit = parseFloat(factorData.iqr_upper);  // 👈 后端传来 IQR 上界
    const names = factorData.name;
    const impact = parseNumeric(factorData.impact_factors);
    const realtime = parseNumeric(factorData.real_time_if);
    const fiveyear = parseNumeric(factorData.five_year_if);
    const hindex = parseNumeric(factorData.h_index);

    function render(showOutliers = true) {
        console.log(upperLimit)
        const filtered = [];
        for (let i = 0; i < names.length; i++) {
            const ifVal = impact[i];
            const pass = showOutliers || (ifVal < upperLimit);
            if (pass) {
                filtered.push({
                    name: names[i],
                    impact: ifVal,
                    realtime: realtime[i],
                    fiveyear: fiveyear[i],
                    hindex: hindex[i]
                });
            }
        }

        myChart.setOption({
            title: {text: '影响力Top 100 期刊'},
            tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
            legend: {data: ['影响因子', '实时IF', '五年IF', 'H-Index']},
            grid: {bottom: 160},
            toolbox: {
                show: true,
                feature: {
                    saveAsImage: {},       // 保存为图片
                    restore: {},           // 还原
                    dataView: {},           // 数据视图，可编辑
                    dataZoom: {},         // 区域缩放（仅在 xAxis 为类目轴时生效）
                    magicType: {type: ['line', 'bar', 'stack']}, // 切换为折线图/柱状图
                }
            },
            xAxis: {
                type: 'category',
                data: filtered.map(d => d.name),
                axisLabel: {rotate: 45}
            },
            yAxis: [
                {type: 'value', name: 'IF类指标', position: 'left'},
                {
                    type: 'value', name: 'H-Index', position: 'right',
                    axisLine: {lineStyle: {color: '#EE6666'}},
                }
            ],
            dataZoom: [
                {type: 'inside', xAxisIndex: 0, start: 0, end: 20},
                {type: 'slider', xAxisIndex: 0, start: 0, end: 20},
            ],
            series: [
                {name: '影响因子', type: 'bar', data: filtered.map(d => d.impact), yAxisIndex: 0},
                {name: '实时IF', type: 'bar', data: filtered.map(d => d.realtime), yAxisIndex: 0},
                {name: '五年IF', type: 'bar', data: filtered.map(d => d.fiveyear), yAxisIndex: 0},
                {name: 'H-Index', type: 'bar', data: filtered.map(d => d.hindex), yAxisIndex: 1}
            ]
        });
    }

    render(true);  // 默认显示所有

    const toggle = document.getElementById('toggleOutliers');
    if (toggle) {
        toggle.addEventListener('change', () => {
            render(toggle.checked);
        });
    }
}


function subject(subjectData, domId = 'subject') {
    const chartDom = document.getElementById(domId);
    const myChart = echarts.init(chartDom);

    const majorData = subjectData.majors;
    const minorMap = subjectData.minors;

    const sortedMajor = [...majorData].sort((a, b) => b.value - a.value);
    const topN = 30;
    const topMajor = sortedMajor.slice(0, topN);

    let inMinorView = false;

    function showMajorChart() {
        myChart.setOption({
            title: {text: '期刊学科分布（点击进入小类）', left: 'center'},
            tooltip: {trigger: 'item'},
            toolbox: {
                show: true,
                feature: {
                    saveAsImage: {},       // 保存为图片
                    restore: {},           // 还原
                    dataView: {},           // 数据视图，可编辑
                    dataZoom: {},         // 区域缩放（仅在 xAxis 为类目轴时生效）
                    magicType: {type: ['line', 'bar', 'stack']}, // 切换为折线图/柱状图
                }
            },
            legend: {
                type: 'scroll',
                orient: 'vertical',
                left: 'left',
            },
            series: [{
                name: '大类学科',
                type: 'pie',
                radius: [30, 120],
                roseType: 'radius', //area radius
                data: topMajor
            }]
        });
    }

    function showMinorChart(majorName) {
        const minors = minorMap[majorName] || [];
        myChart.setOption({
            title: {text: `${majorName} - 小类分布（点击返回）`, left: 'center'},
            tooltip: {trigger: 'item'},
            toolbox: {
                show: true,
                feature: {
                    saveAsImage: {},       // 保存为图片
                    restore: {},           // 还原
                    dataView: {},           // 数据视图，可编辑
                    dataZoom: {},         // 区域缩放（仅在 xAxis 为类目轴时生效）
                    magicType: {type: ['line', 'bar', 'stack']}, // 切换为折线图/柱状图
                }
            },
            legend: {
                type: 'scroll',
                orient: 'vertical',
                left: 'left',
            },
            series: [{
                name: '小类',
                type: 'pie',
                radius: ['30%', '70%'],
                data: minors
            }]
        });
    }

    // 初始加载
    showMajorChart();

    // 点击切换
    myChart.on('click', function (params) {
        if (!inMinorView) {
            const selectedMajor = params.name;
            if (minorMap[selectedMajor]) {
                inMinorView = true;
                showMinorChart(selectedMajor);
            }
        } else {
            inMinorView = false;
            showMajorChart();
        }
    });
}

function citeIf(citeIfData, domId = 'cite_if') {
    const chartDom = document.getElementById(domId);
    const myChart = echarts.init(chartDom);

    myChart.setOption({
        title: {
            text: '期刊自引率 vs 影响因子',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: (p) => `${p.data.name}<br/>IF: ${p.data.value[0]}<br/>自引率: ${p.data.value[1]}%`
        },
        toolbox: {
            show: true,
            feature: {
                saveAsImage: {},       // 保存为图片
                restore: {},           // 还原
                dataView: {},           // 数据视图，可编辑
                dataZoom: {},         // 区域缩放（仅在 xAxis 为类目轴时生效）
                magicType: {type: ['line', 'bar', 'stack']}, // 切换为折线图/柱状图
            }
        },
        xAxis: {
            name: '影响因子',
            type: 'value',
            splitLine: {show: true}
        },
        yAxis: {
            name: '自引率 (%)',
            type: 'value',
            splitLine: {show: true}
        },
        dataZoom: [
            {type: 'inside', xAxisIndex: 0, start: 0, end: 10},
            {type: 'slider', xAxisIndex: 0, start: 0, end: 10},
            {type: 'slider', yAxisIndex: 0, start: 0, end: 100},
        ],
        series: [{
            type: 'scatter',
            // symbolSize: 10,
            data: citeIfData
        }]
    });
}



