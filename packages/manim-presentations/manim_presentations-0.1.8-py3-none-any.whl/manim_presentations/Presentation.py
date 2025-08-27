from manim import *

from manim_presentations import ModularSlide


class Presentation(ModularSlide):
	"""
	A modular slide presentation class with chapter progress tracking.

	Features:
	- Chapter-based organization with progress bars
	- Real-time chapter progress visualization
	- Automatic slide numbering and metadata display
	"""

	def __init__(self, title="My Presentation", short_title=None, subtitle="Subtitle", first_author="Author", other_authors=None,
	             event=None, year=None, chapters=None, title_color=WHITE, title_weight=BOLD, chapter_color=WHITE):
		super().__init__(self)

		self.title = title
		if short_title is not None:
			self.short_title = short_title
		else:
			self.short_title = title.replace("\n", "")[:35]+"..."
		self.subtitle = subtitle
		self.first_author = first_author
		self.other_authors = other_authors if other_authors is not None else []
		self.event = event
		self.year = year
		if chapters is None:
			raise ValueError("Presentation must contain at least one chapter")
		self.chapters = chapters if chapters is not None else []
		for chapter in self.chapters:
			chapter.ctx = self  # Assign presentation as context of the chapter
		self.current_chapter_index = 0
		self.current_slide = 1
		self.inner_canvas = Group()  # Initialize the canvas for the presentation

		# Styling
		self.title_color = title_color
		self.title_weight = title_weight
		self.chapter_color = chapter_color

		# Progress bar styling
		self.bar_height = 0.05  # Height of the progress bar
		self.bar_padding = 0.25  # Padding around the progress bar

		# Build UI elements
		self.chapter_bars = self.build_chapter_bars()
		self.chapter_title = self.build_chapter_title()
		self.current_chapter_progress = self.build_current_chapter_progress()
		self.sub_text = self.build_sub_text()
		self.slide_number = self.build_slide_number()

	def next_slide(self, incr=False, **kwargs):
		"""Advance to the next slide and update progress indicators."""
		self.wait(0.1)

		slide_number_anim, progress_anim = None, None

		if incr:
			self.current_slide += 1

			# Prepare animations for UI updates
			slide_number_anim = self.update_slide_number(return_animation=True)

			# If it was not the last slide of the chapter, update progress bar
			if self.chapters[self.current_chapter_index].current_scene_index < len(self.chapters[self.current_chapter_index].scenes)-1:
				# Regular slide transition within chapter
				progress_anim = self.update_current_chapter_progress(return_animation=True)

			current_chapter = self.chapters[self.current_chapter_index]

			# Recover next scene notes if they exist
			if self.current_chapter_index < len(self.chapters) and \
				current_chapter.current_scene_index < len(current_chapter.scenes)-1:
				next_scene = current_chapter.scenes[current_chapter.current_scene_index+1]
				if hasattr(next_scene, 'notes') and next_scene.notes:
					kwargs['notes'] = next_scene.notes

		else:
			# Recover current scene notes if they exist
			current_chapter = self.chapters[self.current_chapter_index]
			current_scene = current_chapter.scenes[current_chapter.current_scene_index]
			if hasattr(current_scene, 'notes') and current_scene.notes:
				kwargs['notes'] = current_scene.notes

		# Trigger next slide
		super().next_slide(**kwargs)

		animations_to_play = [anim for anim in [slide_number_anim, progress_anim] if anim is not None]
		if animations_to_play:
			self.play(*animations_to_play, run_time=0.2)

	def build_chapter_title(self):
		"""Create the chapter title text element."""
		chapter_title_text = Text(f"{self.chapters[self.current_chapter_index].chapter_short_title}",
		                          font_size=20,
		                          color=self.title_color,
		                          weight=self.title_weight).to_edge(UP, buff=0.15).align_to(self.chapter_bars, LEFT)
		return chapter_title_text

	def update_chapter_title(self, return_animation=False):
		"""Update the chapter title display."""
		new_chapter_title_text = Text(f"{self.chapters[self.current_chapter_index].chapter_short_title}",
		                              font_size=20,
		                              color=self.title_color,
		                              weight=self.title_weight).to_edge(UP, buff=0.15).align_to(self.chapter_bars, LEFT)
		if not return_animation:
			self.play(Transform(self.chapter_title, new_chapter_title_text), run_time=0.15)
			return None
		else:
			return Transform(self.chapter_title, new_chapter_title_text)

	def show_chapter_title(self):
		"""Show the chapter title text."""
		self.chapter_title.set_opacity(1.0)

	def hide_chapter_title(self):
		"""Hide the chapter title text."""
		self.chapter_title.set_opacity(0.0)

	def build_slide_number(self):
		"""Create the slide number text element."""
		slide_nb_text = Text(f"{self.current_slide}",
		                     font_size=24,
		                     color=self.title_color,
		                     weight=self.title_weight).to_corner(DR, buff=0.15)
		return slide_nb_text

	def update_slide_number(self, return_animation=True):
		"""Update the slide number display."""
		new_slide_nb_text = Text(f"{self.current_slide}",
		                         font_size=24,
		                         color=self.title_color,
		                         weight=self.title_weight).to_corner(DR, buff=0.15)
		if not return_animation:
			self.play(Transform(self.slide_number, new_slide_nb_text), run_time=0.15)
			return None
		else:
			return Transform(self.slide_number, new_slide_nb_text)

	def show_slide_number(self):
		"""Show the slide number text."""
		self.slide_number.set_opacity(0.7)

	def hide_slide_number(self):
		"""Hide the slide number text."""
		self.slide_number.set_opacity(0.0)

	def build_sub_text(self):
		"""Create the footer text with presentation metadata."""
		title_text = Text(self.short_title, font_size=16, color=self.title_color)
		first_author_text = Text(self.first_author, font_size=16, color=self.title_color, weight=SEMIBOLD)
		event_text = Text(self.event, font_size=16, color=self.title_color, slant=ITALIC) if self.event else None
		year_text = Text(self.year, font_size=16, color=self.title_color) if self.year else None

		elements = [elem for elem in [title_text, first_author_text, event_text, year_text] if elem is not None]
		sub_text = VGroup(*elements).arrange(RIGHT, buff=0.25).to_corner(DL, buff=0.15)

		return sub_text

	def show_sub_text(self):
		"""Show the footer text."""
		self.sub_text.set_opacity(0.7)

	def hide_sub_text(self):
		"""Hide the footer text."""
		self.sub_text.set_opacity(0.0)

	def build_chapter_bar(self, bar_width):
		"""Create a single chapter progress bar."""
		return RoundedRectangle(
			width=bar_width,
			height=self.bar_height,
			corner_radius=self.bar_height / 2,
			fill_opacity=0.5,
			fill_color=self.chapter_color,
			stroke_width=0
		)

	def build_chapter_bars(self):
		"""Create all chapter progress bars arranged horizontally."""
		# Calculate bar width to fit screen width
		total_bar_length = 14 - (len(self.chapters) + 1) * self.bar_padding
		bar_width = total_bar_length / len(self.chapters)

		chapter_bars = VGroup()
		for i in range(len(self.chapters)):
			chapter_bars.add(self.build_chapter_bar(bar_width))

		# Position at the top of the screen
		chapter_bars.arrange(RIGHT, buff=self.bar_padding).to_edge(UP, buff=.5)
		return chapter_bars

	def update_chapter_bars(self, return_animation=True):
		"""Highlight the current chapter bar."""
		current_bar = self.chapter_bars[self.current_chapter_index]
		if not return_animation:
			self.play(current_bar.animate.set_fill(opacity=1.0), run_time=0.15)
			return None
		else:
			return current_bar.animate.set_fill(opacity=1.0)

	def show_chapter_bars(self):
		"""Show all chapter bars with current chapter highlighted."""
		self.chapter_bars.set_opacity(0.5)
		self.update_chapter_bars()  # Set current chapter bar to full opacity

	def hide_chapter_bars(self):
		"""Hide all chapter bars."""
		self.chapter_bars.set_opacity(0.0)

	def build_current_chapter_progress(self):
		"""Create the green progress bar for the current chapter."""
		if not self.chapters:
			return None

		# Initial width: 1/N of the chapter bar width
		current_chapter_slides = len(self.chapters[self.current_chapter_index].scenes)
		initial_width = self.chapter_bars[self.current_chapter_index].width / current_chapter_slides

		progress_bar = RoundedRectangle(
			width=initial_width,
			height=self.bar_height,
			corner_radius=self.bar_height,
			fill_opacity=1.0,
			fill_color=GREEN,
			stroke_width=0
		)

		# Position on top of the current chapter bar
		current_chapter_bar = self.chapter_bars[self.current_chapter_index]
		progress_bar.move_to(current_chapter_bar)
		progress_bar.align_to(current_chapter_bar.get_left(), LEFT)

		return progress_bar

	def update_current_chapter_progress(self, return_animation=True):
		"""Update the width of the current chapter progress bar."""
		if not self.chapters or not self.current_chapter_progress:
			return None

		current_chapter_slides = len(self.chapters[self.current_chapter_index].scenes)
		current_chapter_bar = self.chapter_bars[self.current_chapter_index]

		# Calculate new width based on chapter progress
		new_width = (current_chapter_bar.width / current_chapter_slides) * (self.chapters[self.current_chapter_index].current_scene_index+2)

		# Create new progress bar with updated width
		new_progress_bar = RoundedRectangle(
			width=new_width,
			height=self.bar_height,
			corner_radius=self.bar_height,
			fill_opacity=1.0,
			fill_color=GREEN,
			stroke_width=0
		)

		# Position correctly on top of the current chapter bar
		new_progress_bar.move_to(current_chapter_bar)
		new_progress_bar.align_to(current_chapter_bar.get_left(), LEFT)

		if not return_animation:
			self.play(Transform(self.current_chapter_progress, new_progress_bar), run_time=0.15)
			return None
		else:
			return Transform(self.current_chapter_progress, new_progress_bar)

	def show_current_chapter_progress(self):
		"""Show the current chapter progress bar."""
		if self.current_chapter_progress:
			self.current_chapter_progress.set_opacity(1.0)

	def hide_current_chapter_progress(self):
		"""Hide the current chapter progress bar."""
		if self.current_chapter_progress:
			self.current_chapter_progress.set_opacity(0.0)

	def build_presentation_intro(self):
		"""Create the presentation title slide content."""
		title_text = Paragraph(self.title, alignment="center", font_size=48, color=self.title_color)
		subtitle_text = Text(self.subtitle, font_size=36, color=self.title_color, weight=self.title_weight)
		authors_full_str = self.first_author + ((", " + ", ".join(self.other_authors)) if self.other_authors else "")
		authors_text = Text(authors_full_str, font_size=24, color=self.title_color,
		                    t2w={self.first_author: self.title_weight}).set_opacity(0.7)

		all_elems = VGroup(title_text, subtitle_text, authors_text).arrange(DOWN, buff=1)
		return all_elems

	def build_chapter_intro(self):
		"""Create the chapter introduction slide content."""
		chapter_title_text = Text(self.chapters[self.current_chapter_index].chapter_title, font_size=36, color=self.title_color, weight=self.title_weight)
		chapter_short_title_text = Text(self.chapters[self.current_chapter_index].chapter_short_title, font_size=24,
		                                color=self.title_color, weight=self.title_weight).set_opacity(0.7)

		all_elems = VGroup(chapter_title_text, chapter_short_title_text).arrange(DOWN, buff=0.2)
		return all_elems

	def build_presentation_conclusion(self):
		"""Create the presentation conclusion slide content."""
		conclusion_text = Text("Thank you for your attention!", font_size=36, color=self.title_color, weight=self.title_weight)
		authors_full_str = self.first_author + ((", " + ", ".join(self.other_authors)) if self.other_authors else "")
		authors_text = Text(authors_full_str, font_size=24, color=self.title_color,
		                    t2w={self.first_author: self.title_weight}).set_opacity(0.7)

		all_elems = VGroup(conclusion_text, authors_text).arrange(DOWN, buff=0.2)
		return all_elems

	def chapter_intro(self):
		"""Display chapter introduction with UI transitions."""
		# Hide UI elements during chapter transition
		self.hide_chapter_title()
		self.hide_chapter_bars()
		self.hide_current_chapter_progress()
		self.hide_sub_text()
		self.hide_slide_number()

		# Show chapter introduction
		chapter_elems = self.build_chapter_intro()
		self.play(FadeIn(chapter_elems), run_time=0.5)

		# Recover first scene notes if they exist
		current_chapter = self.chapters[self.current_chapter_index]
		if hasattr(current_chapter.scenes[0], 'notes') and current_chapter.scenes[0].notes:
			notes = current_chapter.scenes[0].notes
		else:
			notes = ""

		super().next_slide(notes=notes)  # Original next_slide call without increment
		self.play(FadeOut(chapter_elems), run_time=0.25)

		# Rebuild progress bar for the new chapter
		self.chapter_bars.become(self.build_chapter_bars())
		self.chapter_title.become(self.build_chapter_title())
		self.current_chapter_progress.become(self.build_current_chapter_progress())

		"""
		self.play(self.update_chapter_title(return_animation=True),
		          self.update_chapter_bars(return_animation=True),
		          self.update_current_chapter_progress(return_animation=True),
		          run_time=0.2)
		"""

		# Restore UI elements
		self.show_chapter_title()
		self.show_chapter_bars()
		self.show_current_chapter_progress()
		self.show_sub_text()
		self.show_slide_number()

	def presentation_intro(self):
		"""Display the presentation introduction slide."""
		intro_elems = self.build_presentation_intro()
		self.play(FadeIn(intro_elems), run_time=0.5)
		super().next_slide()
		self.play(FadeOut(intro_elems), run_time=0.25)

	def presentation_conclusion(self):
		"""Display the presentation conclusion slide."""
		conclusion_elems = self.build_presentation_conclusion()
		self.play(FadeIn(conclusion_elems), run_time=0.5)

	def construct(self):
		"""Main presentation construction sequence."""
		# Start with presentation introduction
		self.presentation_intro()

		# Add persistent UI elements to foreground
		self.add_foreground_mobjects(self.chapter_title,
		                             self.chapter_bars,
		                             self.current_chapter_progress,
		                             self.sub_text,
		                             self.slide_number)

		# Execute all chapters
		for i, chapter in enumerate(self.chapters):
			self.current_chapter_index = i
			
			# Show first chapter introduction
			self.chapter_intro()
			
			chapter.setup()
			chapter.construct()
			chapter.tear_down()

		# End with conclusion
		self.clear()
		self.presentation_conclusion()
