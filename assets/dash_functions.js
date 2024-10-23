window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // reset_board: function updatePuzzle(puzzle) {
        //     const side = puzzle.length;
        //
        //     // Helper function to check if a value is within the valid range
        //     function isValidValue(value) {
        //         return value >= 1 && value <= side;
        //     }
        //
        //     // Iterate through each cell in the puzzle
        //     for (let row = 0; row < side; row++) {
        //         for (let col = 0; col < side; col++) {
        //             const cellValue = puzzle[row][col];
        //             const cellId = `${row}-${col}`;
        //             const cellProps = isValidValue(cellValue)
        //                 ? {value: cellValue, disabled: true}
        //                 : {value: '', disabled: false};
        //             dash_clientside.set_props(cellId, cellProps);
        //         }
        //     }
        //     return dash_clientside.no_update;
        // }

        reset_board: function updatePuzzle(puzzle) {
            const side = puzzle.length;

            // Precompute cell elements to reduce repeated DOM access
            const elements = {};
            for (let row = 0; row < side; row++) {
                for (let col = 0; col < side; col++) {
                    const cellId = `${row}-${col}`;
                    elements[cellId] = document.getElementById(cellId);
                }
            }

            // Update cell values and states based on the puzzle
            for (let row = 0; row < side; row++) {
                for (let col = 0; col < side; col++) {
                    const cellValue = puzzle[row][col];
                    const cellId = `${row}-${col}`;
                    const element = elements[cellId];

                    if (element) {
                        const isValid = cellValue >= 1 && cellValue <= side;
                        element.value = isValid ? cellValue : '';
                        element.disabled = isValid;
                    }
                }
            }
            return dash_clientside.no_update;
        }
    }
});