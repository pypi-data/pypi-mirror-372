from manim import *
from manim_slides import Slide

from manim_presentations import ModularSlide


class Chapter(ModularSlide):
	def __init__(self, ctx=None, chapter_title="Chapter", chapter_short_title="Chapter"):
		if ctx:
			# update self so that methods of the parent Presentation class have priority
			self.ctx = ctx
		else:
			self.ctx = self
			self.inner_canvas = Group()

		super().__init__(self.ctx)

		self.scenes = []
		self.chapter_title = chapter_title
		self.chapter_short_title = chapter_short_title
		self.current_scene_index = 0  # To track the current scene index

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


	def setup(self):
		pass

	def construct(self):
		ctx = self.ctx

		for i, scene in enumerate(self.scenes):
			self.current_scene_index = i
			scene.setup(ctx)
			scene.construct(ctx)
			ctx.next_slide(incr=True)
			scene.tear_down(ctx)


	def tear_down(self):
		# By default, clear the canvas after the chapter is done
		# print("Clearing canvas for chapter", self.chapter_title)
		# print(f"Content: {self.inner_canvas.submobjects}")
		# print(f"Content: {self.ctx.inner_canvas.submobjects}")
		# print(f"{self.__dict__}")
		self.ctx.remove(*self.ctx.inner_canvas.submobjects)
