# ManimPresentations

This is a minimal and quick-and-dirty package to make ManimSlides more modular and reduce the time
required to create presentations. It unifies the way presentations are created and displayed. It allows composition
of chapters as list of slides and of presentations as list of chapters. That way, your slides and chapters
can be reused in different presentations. Furthermore, it allows to render individual slides and chapters, so
you don't have to render the whole presentation every time you want to see a change.

## Main objectives:

* have a clear hierarchy: presentation -> chapters -> slides
* have shared elements between slides (slide number, presentation title, author, year, event, current chapter, etc.)
* being able to compose Presentations using various chapters and slides
* being able to render and launch the whole presentation with the usual `manim-slides render example.py MyPresentation` 
and `manim-slides MyPresentation` commands
* provide an elegant layout for presentations

## State of the project:

This is a _personal project_ that I started to make my life easier when creating presentations with Manim. It may be
useful to others, but do not consider it a complete, elegant or polished solution. It probably lacks a lot of useful 
features to make it a general tool, but it's not my intention to make it so :)

If you have suggestions, ideas or feedback, feel free to open a discussion though!

## Installation:

You can install this package using pip:

```bash
pip install manim-presentations
```

To install locally, you can clone the repository and run:

```bash
pip install -e .
```

## Components:

### ModularSlide

A `ModularSlide` is a single slide in a presentation. It extends the `manim_slides.Slide` class, so it's a Manim Scene.

The magic is in the `ctx` context argument that is passed to the `__init__` method. By default this context is None,
in which case the slide behaves like a normal Manim Scene/Slide, allowing you to use it as a standalone scene. But this
context can also be an instance of `manim_presentations.Presentation` or `manim_presentations.Chapter`, which allows
rendering the slide within the presentation or chapter.

A `ModularSlide` also contains an `inner_canvas` attribute, which is a `manim.Group` intended to contain the graphical
elements of the slide. The default `tear_down` method clears this inner canvas, but can be overridden by your custom
slide class. This allows you to create slides that reuse the canvas from a previous slide, although this requires
knowing how the previous slide organised its canvas in the first place.

### Chapter

A chapter is a portion of a presentation that can be composed of multiple `ModularSlides`. By default, its `construct`
method iterates over the slides and renders them one by one.

It also receives a `ctx` context argument, which can be an instance of `manim_presentations.Presentation` but is None
by default. This allows to render a chapter as a standalone scene, or as part of a presentation.

### Presentation

A presentation is the actual, complete presentation that you want to create. It receives chapters as a list of `Chapter` 
instances and renders them in the order they are provided. 

It has properties like the title, presenting author, other authors, year, event it is made for, and a list of chapters.

It implements various methods for:
* introduction and conclusion slides
* building, showing, hiding and updating various layout elements like slide number, chapter progression or sub-text.
* ...
