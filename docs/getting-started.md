# Getting Started

Here's a quick guide on MathLamp to get you started

!!! warning

    MathLamp needs to be installed before following this tutorial, if you don't have Mathlamp installed see [Installing](installing.md).

First open a MathLamp REPL with `python main.py`,  
You should see a `>` in the console

The REPL is where you can type expressions, and it will show you the result.

## Operations

MathLamp can evaluate operations such as:
```
> 1 + 1 // Outputs 2.0
> 2 - 1 // Outputs 1.0
> 3 * 2 // Outputs 6.0
> 6 / 2 // Outputs 3.0
```

!!! note

    In the code examples you may notice the two forward slashes `//`, they mean a comment,  
    MathLamp will always ignore comments. Use them to explain your code!

## Printing output

When running a file, unlike the REPL, values will be only printed to the console if they are on an out() statement:
```
// example.lmp
out[1 + 1] // Outputs 2.0
2 + 2 // Outputs nothing
```

## Variables

You can use variables to store values:
```
> x = 3
> x // Outputs 3.0
```
Or use them in operations:
```
> y = 5
> y + 3 // Outputs 8.0
```