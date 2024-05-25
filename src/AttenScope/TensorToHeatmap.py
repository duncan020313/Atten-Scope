import numpy as np
import random
from typing import Iterable


def generate_heatmap_html(matrices: Iterable[np.ndarray], labels, tokens):
    rows, cols = matrices[0].shape
    hues = [random.randint(0, 360) for _ in matrices]  # Random hue for each matrix
    min_vals = [np.min(matrix[np.isfinite(matrix)]) for matrix in matrices]
    max_vals = [np.max(matrix) for matrix in matrices]
    data_arrays = [matrix.tolist() for matrix in matrices]

    # Generate preview canvases
    preview_canvases = []
    for idx, matrix in enumerate(matrices):
        hue = hues[idx]
        preview_canvas = f'<canvas id="previewCanvas{idx}" width="50" height="50"></canvas><br>{labels[idx]}'
        preview_canvases.append(preview_canvas)

    # Token sequence with line breaks
    token_sequence = "".join(
        [
            (
                f'<span class="token" id="token{i}" onmouseover="highlightRowOrColumnAndToken({i})" onclick="toggleFixRowOrColumn({i})">\\n</span><br>'
                if token == "\n"
                else f'<span class="token" id="token{i}" onmouseover="highlightRowOrColumnAndToken({i})" onclick="toggleFixRowOrColumn({i})">{token}</span>'
            )
            for i, token in enumerate(tokens)
        ]
    )

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Matrix Heatmap</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
        }}
        .viewer {{
            display: flex;
            flex-direction: row;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 100%;
        }}
        #buttons {{
            margin-bottom: 10px;
        }}
        .button {{
            display: inline-block;
            margin-right: 5px;
            cursor: pointer;
            text-align: center;
        }}
        .button {{
            border: 1px solid black;
        }}
        .button.neon {{
            box-shadow: 0 0 10px #00f, 0 0 20px #00f, 0 0 30px #00f, 0 0 40px #00f;
        }}
        .token {{
            display: inline-block;
            cursor: pointer;
            margin: 2px 0;
        }}
        .token:hover {{
            text-decoration: underline;
        }}
        #tokens {{
            margin-left: 20px;
            word-wrap: break-word;
            font-size: 30px;
        }}
        .canvas-wrapper {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: min(75vw, 75vh);
            height: min(75vw, 75vh);
        }}
        canvas {{
            width: 100%;
            height: 100%;
        }}
        .token-viewer {{
            display: flex;
            flex-direction: column;
            justify-content: top;
            align-items: center;
            width: 25vw;
            height: 75vh;
            overflow-y: auto;
        }}
        .mode-buttons {{
            margin-bottom: 10px;
        }}
        .mode-button {{
            cursor: pointer;
            padding: 5px 10px;
            margin-right: 5px;
            border: 1px solid black;
            border-radius: 3px;
        }}
        .mode-button.active {{
            background-color: #00f;
            color: #fff;
        }}
    </style>
</head>
<body>
<div id="buttons">
    {''.join([f'<div class="button" id="button{i}" onmouseover="showMatrix({i}, true)" onclick="toggleFixMatrix({i})">{preview_canvases[i]}</div>' for i in range(len(matrices))])}
</div>
<div class="viewer">
    <div class="canvas-wrapper">
        <canvas id="heatmapCanvas"></canvas>
    </div>
    <div class="token-viewer">
        <div class="mode-buttons">
            <div class="mode-button active" id="rowMode" onclick="setMode('row')">Row Mode</div>
            <div class="mode-button" id="columnMode" onclick="setMode('column')">Column Mode</div>
        </div>
        <div id="tokens">
            {token_sequence}
        </div>
    </div>
</div>
<script>
    const canvas = document.getElementById('heatmapCanvas');
    const ctx = canvas.getContext('2d');
    const matrices = {data_arrays};
    const rows = {rows};
    const cols = {cols};
    const minVals = {min_vals};
    const maxVals = {max_vals};
    const hues = {hues};
    let fixedMatrixIndex = null;
    let currentMatrixIndex = 0;
    let currentMode = 'row'; // Default mode

    function resizeCanvas() {{
        const canvasWrapper = document.querySelector('.canvas-wrapper');
        canvas.width = canvasWrapper.clientWidth;
        canvas.height = canvasWrapper.clientHeight;
        drawMatrix(currentMatrixIndex);
    }}

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    function valueToColor(value, minVal, maxVal, hue, dim = false) {{
        const normalizedValue = (value - minVal) / (maxVal - minVal);
        const lightness = 100 - Math.floor(normalizedValue * 75);  // lightness from 25% to 100%
        if (dim) {{
            return `hsl(${{hue}}, 0%, ${{lightness}}%)`;  // Dim the brightness for non-highlighted rows
        }}
        return `hsl(${{hue}}, 100%, ${{lightness}}%)`;
    }}

    function drawMatrix(matrixIndex, highlightIndex = null) {{
        const data = matrices[matrixIndex];
        const minVal = minVals[matrixIndex];
        const maxVal = maxVals[matrixIndex];
        const hue = hues[matrixIndex];
        const currentRows = data.length;
        const currentCols = data[0].length;
        const cellWidth = Math.floor(canvas.width / currentCols);
        const cellHeight = Math.floor(canvas.height / currentRows);

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let i = 0; i < currentRows; i++) {{
            for (let j = 0; j < currentCols; j++) {{
                let dim = false;
                if (highlightIndex !== null) {{
                    if (currentMode === 'row' && i !== highlightIndex) {{
                        dim = true;
                    }} else if (currentMode === 'column' && j !== highlightIndex) {{
                        dim = true;
                    }}
                }}
                ctx.fillStyle = valueToColor(data[i][j], minVal, maxVal, hue, dim);
                ctx.fillRect(j * cellWidth, i * cellHeight, cellWidth, cellHeight);
            }}
        }}
    }}

    function showMatrix(matrixIndex, updateTokens = false) {{
        currentMatrixIndex = matrixIndex;
        if (fixedMatrixIndex === null) {{
            drawMatrix(matrixIndex);
        }}
        if (updateTokens) {{
            const rowOrColumn = matrices[matrixIndex][0];
            const minVal = minVals[matrixIndex];
            const maxVal = maxVals[matrixIndex];
            const hue = hues[matrixIndex];
            for (let i = 0; i < rowOrColumn.length; i++) {{
                const tokenElem = document.getElementById('token' + i);
                tokenElem.style.backgroundColor = valueToColor(rowOrColumn[i], minVal, maxVal, hue);
            }}
        }}
    }}

    function toggleFixMatrix(matrixIndex) {{
        if (fixedMatrixIndex === matrixIndex) {{
            fixedMatrixIndex = null;
            document.getElementById('button' + matrixIndex).classList.remove('neon');
        }} else {{
            fixedMatrixIndex = matrixIndex;
            // Remove neon effect from all buttons
            for (let i = 0; i < matrices.length; i++) {{
                document.getElementById('button' + i).classList.remove('neon');
            }}
            // Add neon effect to the selected button
            document.getElementById('button' + matrixIndex).classList.add('neon');
        }}
        drawMatrix(matrixIndex);
    }}

    function highlightRowOrColumnAndToken(index) {{
        if (currentMode === 'row') {{
            highlightRow(index);
        }} else {{
            highlightColumn(index);
        }}
        highlightToken(index);
    }}

    function highlightRow(rowIndex) {{
        const matrixIndex = fixedMatrixIndex !== null ? fixedMatrixIndex : currentMatrixIndex;
        drawMatrix(matrixIndex, rowIndex);
    }}

    function highlightColumn(colIndex) {{
        const matrixIndex = fixedMatrixIndex !== null ? fixedMatrixIndex : currentMatrixIndex;
        drawMatrix(matrixIndex, colIndex);
    }}

    function highlightToken(index) {{
        const matrixIndex = fixedMatrixIndex !== null ? fixedMatrixIndex : currentMatrixIndex;
        const minVal = minVals[matrixIndex];
        const maxVal = maxVals[matrixIndex];
        const hue = hues[matrixIndex];
        let values;
        if (currentMode === 'row') {{
            values = matrices[matrixIndex][index];
        }} else {{
            values = matrices[matrixIndex].map(row => row[index]);
        }}
        for (let i = 0; i < values.length; i++) {{
            const tokenElem = document.getElementById('token' + i);
            tokenElem.style.backgroundColor = valueToColor(values[i], minVal, maxVal, hue);
        }}
    }}

    function toggleFixRowOrColumn(index) {{
        if (fixedMatrixIndex !== null) {{
            if (currentMode === 'row') {{
                highlightRow(index);
            }} else {{
                highlightColumn(index);
            }}
        }}
    }}

    function drawPreview(matrixIndex) {{
        const previewCanvas = document.getElementById('previewCanvas' + matrixIndex);
        const previewCtx = previewCanvas.getContext('2d');
        const data = matrices[matrixIndex];
        const minVal = minVals[matrixIndex];
        const maxVal = maxVals[matrixIndex];
        const hue = hues[matrixIndex];
        const previewRows = previewCanvas.height;
        const previewCols = previewCanvas.width;
        const cellHeight = Math.max(previewCanvas.height / data.length, 2);
        const cellWidth = Math.max(previewCanvas.width / data[0].length, 2);
        const maxIndex = Math.min(previewRows / cellWidth, data.length);
        console.log(cellWidth, cellHeight, maxIndex)
        for (let i = 0; i < maxIndex; i++) {{
            for (let j = 0; j < maxIndex; j++) {{
                previewCtx.fillStyle = valueToColor(data[i][j], minVal, maxVal, hue);
                previewCtx.fillRect(j * cellWidth, i * cellHeight, cellWidth, cellHeight);
            }}
        }}
    }}

    function setMode(mode) {{
        currentMode = mode;
        document.getElementById('rowMode').classList.toggle('active', mode === 'row');
        document.getElementById('columnMode').classList.toggle('active', mode === 'column');
    }}

    // Draw previews
    for (let i = 0; i < matrices.length; i++) {{
        drawPreview(i);
    }}

    // Initial display
    showMatrix(currentMatrixIndex);
</script>
</body>
</html>
    """
    return html_content
