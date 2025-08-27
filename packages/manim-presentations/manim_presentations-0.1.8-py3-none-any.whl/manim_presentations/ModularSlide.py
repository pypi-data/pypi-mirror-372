from manim import *
from manim_slides import Slide


class ModularSlide(Slide):
	"""
	Abstract class for a modular slide. Extend it with a construct() method to build your slide.
	"""
	skip_reversing = True
	notes = None

	def __init__(self, ctx=None, **kwargs):
		super().__init__(**kwargs)  # TODO: Check if the `renderer` kwarg is similar to our `ctx` parameter
		if ctx:
			# update self so that methods of the parent Presentation class have priority
			self.ctx = ctx
		else:
			self.ctx = self
			self.inner_canvas = Group()

	def next_slide(self, incr=False, **kwargs):
		"""
		Override the `next_slide` method to allow incrementing the slide_number when we are in the context of a
		Presentation. By default, incr is False, meaning that we use next_slide() more as a pause in the
		animation of a specific slide, rather than a real step in the presentation.
		"""
		self.wait(0.1)
		# Late import to avoid circular import issues
		from manim_presentations import Presentation

		if incr and type(self.ctx) is Presentation:
			self.ctx.next_slide(incr=incr, **kwargs)
		else:
			super().next_slide(**kwargs)  # Default manim-slides behavior

	def construct(self):
		# N.b: if called from a Presentation, the canvas might already be added to the Presentation's canvas
		self.add(self.inner_canvas)

	def tear_down(self):
		# By default, clear the canvas after the slide is done
		# print(f"Clearing canvas for {self.__class__.__name__}, content: {self.inner_canvas.submobjects}")
		self.remove(*self.inner_canvas.submobjects)
