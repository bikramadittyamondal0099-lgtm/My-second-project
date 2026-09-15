def square_sum(
    a,
    b
):

    return (
        a * a
        +
        b * b
    )


def complex_math(
    numbers
):

    total = 0

    for number in numbers:

        total += number ** 2

    return {

        "count":
            len(numbers),

        "sum_of_squares":
            total,

        "average":
            total / len(numbers)
            if numbers
            else 0
    }


def matrix_sum(
    matrix
):

    total = 0

    for row in matrix:

        for value in row:

            total += value

    return total