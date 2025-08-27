#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 26/08/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

from pathlib import Path
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle

import numpy as np

#===== Loading Devanagari font ========
def _load_devanagari_font():
	"""
	Load devanagari font as it works for both English and Hindi.
	"""
	
	# Path to your bundled font
	font_path = Path(__file__).resolve().parents[1] / "fonts" / "NotoSansDevanagari-Regular.ttf"
	
	# Register the font with matplotlib
	fm.fontManager.addfont(str(font_path))
	
	# Get the font family name from the file
	hindi_font = fm.FontProperties(fname=str(font_path))
	
	# Set as default rcParam
	mpl.rcParams['font.family'] = hindi_font.get_name()
	
_load_devanagari_font()
#==============

#--------------------------
# Figuure 1D
#--------------------------
class Figure1D:
	"""
	A utility class that provides easy-to-use API
	for plotting 1D signals along with clean
	representations of annotations, events.

	

	Parameters
	----------
	n_aux_subplots: int
		- Total number of auxiliary subplots
		- These include annotations and events subplots.
		- Default: 0
	title: str
		- Title of the figure.
		- Default: Title
	xlim: tuple[number, number]
		- xlim for the figure.
		- All subplots will be automatically adjusted.
		- Default: None
	ylim: tuple[number, number]
		- ylim for the signal.
		- Default: None
	"""
	
	def __init__(self, n_aux_subplots=0, xlim=None, ylim=None):
		self._n_aux_subplots: int = n_aux_subplots
		self._active_subplot_idx: int = 1 # Any addition will happen on this subplot (0 is reserved for reference axis)
		self._xlim = xlim # Many add functions depend on this, so we fix it while instantiating the class
		self._ylim = ylim
		self._subplots, self._fig = self._generate_subplots() # Will contain all the subplots (list, fig)
	
	def _get_active_subplot(self):
		"""
		Get the active subplot where you can add
		either annotations or events.
		"""
		active_subplot = self._subplots[self._active_subplot_idx]
		self._active_subplot_idx += 1
		
		return active_subplot
		
	def _generate_subplots(self):
		"""
		Generate subplots based on the configuration.
		"""
		
		n_aux_subplots = self._n_aux_subplots
		
		# Fixed heights per subplot type
		ref_height = 0.0
		aux_height = 0.4
		signal_height = 2.0
		
		# Total number of subplots
		n_subplots = 1 + n_aux_subplots + 1
		
		# Compute total fig height
		fig_height = ref_height + n_aux_subplots * aux_height + signal_height
		
		# Define height ratios
		height_ratios = [ref_height] + [aux_height] * n_aux_subplots + [signal_height]
		
		# Create figure and grid
		fig = plt.figure(figsize=(16, fig_height))
		gs = gridspec.GridSpec(n_subplots, 1, height_ratios=height_ratios)
		
		# Add subplots
		subplots_list = []
		ref_subplot = fig.add_subplot(gs[0, 0])
		ref_subplot.axis("off")
		subplots_list.append(ref_subplot)
		
		for i in range(1, n_subplots):
			subplots_list.append(fig.add_subplot(gs[i, 0], sharex=ref_subplot))
			
		for i in range(n_subplots - 1):
			subplots_list[i].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
		
		# Set xlim
		if self._xlim is not None: # xlim should be applied on reference subplot, rest all sharex
			ref_subplot.set_xlim(self._xlim)
			
		# Set ylim
		if self._ylim is not None: # ylim should be applied on the signal subplot
			subplots_list[-1].set_ylim(self._ylim)
									
		fig.subplots_adjust(hspace=0.01, wspace=0.05)
			
		return subplots_list, fig
	
		
	def add_events(self, events, c="k", ls="-", lw=1.5, label="Event Label"):
		"""
		Add events to the figure.
		
		Parameters
		----------
		events: np.ndarray
			- All the event marker values.
		c: str
			- Color of the event marker.
			- Default: "k"
		ls: str
			- Line style.
			- Default: "-"
		lw: float
			- Linewidth.
			- Default: 1.5
		label: str
			- Label for the event type.
			- This will appear in the legend.
			- Default: "Event label"

		Returns
		-------
		None
		"""
		event_subplot = self._get_active_subplot()
		xlim = self._xlim
		
		for i, event in enumerate(events):
			if xlim is not None:
				if xlim[0] <= event <= xlim[1]:
					if i == 0: # Label should be set only once for all the events
						event_subplot.axvline(x=event, color=c, linestyle=ls, linewidth=lw, label=label)
					else:
						event_subplot.axvline(x=event, color=c, linestyle=ls, linewidth=lw)
			else:
				if i == 0: # Label should be set only once for all the events
					event_subplot.axvline(x=event, color=c, linestyle=ls, linewidth=lw, label=label)
				else:
					event_subplot.axvline(x=event, color=c, linestyle=ls, linewidth=lw)
		
	def add_annotation(self, ann):
		"""
		Add annotation to the figure.
		
		Parameters
		----------
		ann : list[tuple[Number, Number, str]] | None
			- A list of annotation spans. Each tuple should be (start, end, label).
			- Default: None (no annotations).
		
		Returns
		-------
		None
		"""
		
		ann_subplot = self._get_active_subplot()
		xlim = self._xlim
		
		for i, (start, end, tag) in enumerate(ann):
			
			# We make sure that we only plot annotation that are within the x range of the current view
			if xlim is not None:
				if start >= xlim[1] or end <= xlim[0]:
					continue
				
				# Clip boundaries to xlim
				start = max(start, xlim[0])
				end = min(end, xlim[1])
				
				box_colors = ["gray", "lightgray"] # Alternates color between two
				box_color = box_colors[i % 2]
				
				width = end - start
				rect = Rectangle((start, 0), width, 1, facecolor=box_color, edgecolor="black", alpha=0.7)
				ann_subplot.add_patch(rect)
				
				text_obj = ann_subplot.text(
					(start + end) / 2, 0.5, tag,
					ha='center', va='center',
					fontsize=10, color="black", fontweight='bold', zorder=10, clip_on=True
				)
				
				text_obj.set_clip_path(rect)
			else:
				box_colors = ["gray", "lightgray"] # Alternates color between two
				box_color = box_colors[i % 2]
				
				width = end - start
				rect = Rectangle((start, 0), width, 1, facecolor=box_color, edgecolor="black", alpha=0.7)
				ann_subplot.add_patch(rect)
				
				text_obj = ann_subplot.text(
					(start + end) / 2, 0.5, tag,
					ha='center', va='center',
					fontsize=10, color="black", fontweight='bold', zorder=10, clip_on=True
				)
				
				text_obj.set_clip_path(rect)
	
	def add_signal(self, y, x=None, c=None, ls="-", lw=1.5, m=None, ms=3, label="Signal"):
		"""
		Add signal to the figure.
			
		Parameters
		----------
		y: np.ndarray
			- Signal y values.
		x: np.ndarray | None
			- Signal x values.
			- Default: None (indices will be used)
		c: str
			- Color of the line.
			- Default: None
		ls: str
			- Linestyle
			- Default: "-"
		lw: Number
			- Linewidth
			- Default: 1
		m: str
			- Marker
			- Default: None
		ms: number
			- Markersize
			- Default: 5
		label: str
			- Label for the plot.
			- Legend will use this.
			- Default: "Signal"

		Returns
		-------
		None
		"""
		if x is None:
			x = np.arange(y.size)
		signal_subplot = self._subplots[-1]
		signal_subplot.plot(x, y, color=c, linestyle=ls, linewidth=lw, marker=m, markersize=ms, label=label)
		
	def add_legend(self, ypos=1.3):
		"""
		Add legend to the figure.

		Parameters
		----------
		ypos: float
			- y position from the top.
			- > 1 to push it higher, < 1 to push it lower
			- Default: 1.3
		
		Returns
		-------
		None
		"""
		subplots: list = self._subplots
		fig = self._fig
		
		all_handles, all_labels = [], []
		
		for subplot in subplots:
			handles, labels = subplot.get_legend_handles_labels()
			all_handles.extend(handles)
			all_labels.extend(labels)
			
		# remove duplicates if needed
		fig.legend(all_handles, all_labels, loc='upper right', bbox_to_anchor=(0.9, ypos), ncol=2, frameon=True, bbox_transform=fig.transFigure)
		
	def add_meta_info(self, title=None, ylabel=None, xlabel=None, ts=13, ls=11):
		"""
		Add meta info to the figure.

		Parameters
		----------
		title: str
			- Title of the figure.
			- Default: None
		ylabel: str
			- y label of the signal.
			- It will only appear in the signal subplot.
			- Default: None
		xlabel: str
			- x label of the signal.
			- It will only appear in the signal subplot.
			- Default: None
		ts: Number
			- Title size
			- Default: 10
		ls: Number
			- Label size.
			- Default: 10
		Returns
		-------
		None
		"""
		subplots: list = self._subplots
		fig = self._fig
		
		ref_subplot = subplots[0]
		signal_subplot = subplots[-1]
		
		if title is not None:
			ref_subplot.set_title(title, pad=10, size=ts)
		if ylabel is not None:
			signal_subplot.set_ylabel(ylabel, size=ls)
		if xlabel is not None:
			signal_subplot.set_xlabel(xlabel, size=ls)
		
		
	def save(self, path="./figure.png"):
		"""
		Save the figure.

		Parameters
		----------
		path: str
			- Path to the output file.

		Returns
		-------
		None
		"""
		fig = self._fig
		fig.savefig(path, bbox_inches="tight")
		

#--------------------------
# Figuure 2D
#--------------------------
class Figure2D:
	"""
	A utility class that provides easy-to-use API
	for plotting 2D signals along with clean
	representations of annotations, events.

	

	Parameters
	----------
	n_aux_subplots: int
		- Total number of auxiliary subplots
		- These include annotations and events subplots.
		- Default: 0
	title: str
		- Title of the figure.
		- Default: Title
	xlim: tuple[number, number]
		- xlim for the figure.
		- All subplots will be automatically adjusted.
		- Default: None
	ylim: tuple[number, number]
		- ylim for the signal.
		- Default: None
	"""
	
	def __init__(self, n_aux_subplots=0, xlim=None, ylim=None):
		self._n_aux_subplots: int = n_aux_subplots
		self._active_subplot_idx: int = 1 # Any addition will happen on this subplot (0 is reserved for reference axis)
		self._xlim = xlim # Many add functions depend on this, so we fix it while instantiating the class
		self._ylim = ylim
		self._subplots, self._fig = self._generate_subplots() # Will contain all the subplots (list, fig)
		self._im = None # Useful while creating colorbar for the image
		
	def _get_active_subplot(self):
		"""
		Get the active subplot where you can add
		either annotations or events.
		"""
		active_subplot = self._subplots[self._active_subplot_idx]
		self._active_subplot_idx += 1
		
		return active_subplot
	
	def _calculate_extent(self, x, y):
		# Handle spacing safely
		if len(x) > 1:
			dx = x[1] - x[0]
		else:
			dx = 1  # Default spacing for single value
		if len(y) > 1:
			dy = y[1] - y[0]
		else:
			dy = 1  # Default spacing for single value
			
		return [x[0] - dx / 2, x[-1] + dx / 2, y[0] - dy / 2, y[-1] + dy / 2]
	
	def _add_colorbar(self, im, label=None, width="20%", height="35%"):
		from mpl_toolkits.axes_grid1.inset_locator import inset_axes
		
		ref_subplot = self._subplots[0]
		
		# Assume ref_subplot is your reference axes, im is the image
		cax = inset_axes(
			ref_subplot,
			width=width,        # width of colorbar
			height=height,        # height of colorbar
			loc='right',
			bbox_to_anchor=(0, 1, 1, 1),  # move 0.9 right, 1.2 up from the subplot
			bbox_transform=ref_subplot.transAxes,  # important: use subplot coords
			borderpad=0
		)
		
		cbar = plt.colorbar(im, cax=cax, orientation='horizontal')
		cbar.ax.xaxis.set_ticks_position('top')
		cbar.set_label(label, labelpad=5)
			
	
		
	def _generate_subplots(self):
		"""
		Generate subplots based on the configuration.
		"""
		
		n_aux_subplots = self._n_aux_subplots
		
		# Fixed heights per subplot type
		ref_height = 0.4
		aux_height = 0.4
		signal_height = 4.0
		
		# Total number of subplots
		n_subplots = 1 + n_aux_subplots + 1
		
		# Compute total fig height
		fig_height = ref_height + n_aux_subplots * aux_height + signal_height
		
		# Define height ratios
		height_ratios = [ref_height] + [aux_height] * n_aux_subplots + [signal_height]
		
		# Create figure and grid
		fig = plt.figure(figsize=(16, fig_height))
		gs = gridspec.GridSpec(n_subplots, 1, height_ratios=height_ratios)
		
		# Add subplots
		subplots_list = []
		ref_subplot = fig.add_subplot(gs[0, 0])
		ref_subplot.axis("off")
		subplots_list.append(ref_subplot)
		
		for i in range(1, n_subplots):
			subplots_list.append(fig.add_subplot(gs[i, 0], sharex=ref_subplot))
			
		for i in range(n_subplots - 1):
			subplots_list[i].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
			
		# Set xlim
		if self._xlim is not None: # xlim should be applied on reference subplot, rest all sharex
			ref_subplot.set_xlim(self._xlim)
		
		# Set ylim
		if self._ylim is not None: # ylim should be applied on the signal subplot
			subplots_list[-1].set_ylim(self._ylim)
		
		fig.subplots_adjust(hspace=0.01, wspace=0.05)
		
		return subplots_list, fig
	
	
	def add_events(self, events, c="k", ls="-", lw=1.5, label="Event Label"):
		"""
		Add events to the figure.
		
		Parameters
		----------
		events: np.ndarray
			- All the event marker values.
		c: str
			- Color of the event marker.
			- Default: "k"
		ls: str
			- Line style.
			- Default: "-"
		lw: float
			- Linewidth.
			- Default: 1.5
		label: str
			- Label for the event type.
			- This will appear in the legend.
			- Default: "Event label"

		Returns
		-------
		None
		"""
		event_subplot = self._get_active_subplot()
		xlim = self._xlim
		
		for i, event in enumerate(events):
			if xlim is not None:
				if xlim[0] <= event <= xlim[1]:
					if i == 0: # Label should be set only once for all the events
						event_subplot.axvline(x=event, color=c, linestyle=ls, linewidth=lw, label=label)
					else:
						event_subplot.axvline(x=event, color=c, linestyle=ls, linewidth=lw)
			else:
				if i == 0: # Label should be set only once for all the events
					event_subplot.axvline(x=event, color=c, linestyle=ls, linewidth=lw, label=label)
				else:
					event_subplot.axvline(x=event, color=c, linestyle=ls, linewidth=lw)
					
	def add_annotation(self, ann):
		"""
		Add annotation to the figure.
		
		Parameters
		----------
		ann : list[tuple[Number, Number, str]] | None
			- A list of annotation spans. Each tuple should be (start, end, label).
			- Default: None (no annotations).
		
		Returns
		-------
		None
		"""
		ann_subplot = self._get_active_subplot()
		xlim = self._xlim
		
		for i, (start, end, tag) in enumerate(ann):
			
			# We make sure that we only plot annotation that are within the x range of the current view
			if xlim is not None:
				if start >= xlim[1] or end <= xlim[0]:
					continue
				
				# Clip boundaries to xlim
				start = max(start, xlim[0])
				end = min(end, xlim[1])
					
				box_colors = ["gray", "lightgray"] # Alternates color between two
				box_color = box_colors[i % 2]
				
				width = end - start
				rect = Rectangle((start, 0), width, 1, facecolor=box_color, edgecolor="black", alpha=0.7)
				ann_subplot.add_patch(rect)
				
				text_obj = ann_subplot.text(
					(start + end) / 2, 0.5, tag,
					ha='center', va='center',
					fontsize=10, color="black", fontweight='bold', zorder=10, clip_on=True
				)
				
				text_obj.set_clip_path(rect)
			else:
				box_colors = ["gray", "lightgray"] # Alternates color between two
				box_color = box_colors[i % 2]
				
				width = end - start
				rect = Rectangle((start, 0), width, 1, facecolor=box_color, edgecolor="black", alpha=0.7)
				ann_subplot.add_patch(rect)
				
				text_obj = ann_subplot.text(
					(start + end) / 2, 0.5, tag,
					ha='center', va='center',
					fontsize=10, color="black", fontweight='bold', zorder=10, clip_on=True
				)
				
				text_obj.set_clip_path(rect)
				
	def add_matrix(self, M, y=None, x=None, c="gray_r", o="lower", label="Matrix"):
		"""
		Add matrix to the figure.
			
		Parameters
		----------
		M: np.ndarray
			- Matrix (2D) array
		y: np.ndarray | None
			- y axis values.
		x: np.ndarray | None (indices will be used)
			- x axis values.
			- Default: None (indices will be used)
		c: str
			- cmap for the matrix.
			- Default: None
		o: str
			- origin
			- Default: "lower"
		label: str
			- Label for the plot.
			- Legend will use this.
			- Default: "Signal"
		
		Returns
		-------
		None
		"""
		if x is None: x = np.arange(M.shape[1])
		if y is None: y = np.arange(M.shape[0])
			
		matrix_subplot = self._subplots[-1]
		extent = self._calculate_extent(x, y)
		im = matrix_subplot.imshow(M, aspect="auto", origin=o, cmap=c, extent=extent)
		
		self._add_colorbar(im=im, label=label)
	
	def add_signal(self, y, x=None, c=None, ls="-", lw=1.5, m="o", ms=3, label="Signal"):
		"""
		Add signal on the matrix.
			
		Parameters
		----------
		y: np.ndarray
			- Signal y values.
		x: np.ndarray | None
			- Signal x values.
			- Default: None (indices will be used)
		c: str
			- Color of the line.
			- Default: None
		ls: str
			- Linestyle
			- Default: "-"
		lw: Number
			- Linewidth
			- Default: 1
		m: str
			- Marker
			- Default: None
		ms: number
			- Markersize
			- Default: 5
		label: str
			- Label for the plot.
			- Legend will use this.
			- Default: "Signal"
		
		Returns
		-------
		None
		"""
		if x is None:
			x = np.arange(y.size)
		matrix_subplot = self._subplots[-1]
		matrix_subplot.plot(x, y, color=c, linestyle=ls, linewidth=lw, marker=m, markersize=ms, label=label)
		
	
			
	def add_legend(self, ypos=1.1):
		"""
		Add legend to the figure.

		Parameters
		----------
		ypos: float
			- y position from the top.
			- > 1 to push it higher, < 1 to push it lower
			- Default: 1.3
		
		Returns
		-------
		None
		"""
		subplots: list = self._subplots
		fig = self._fig
		
		all_handles, all_labels = [], []
		
		for subplot in subplots:
			handles, labels = subplot.get_legend_handles_labels()
			all_handles.extend(handles)
			all_labels.extend(labels)
			
		# remove duplicates if needed
		fig.legend(all_handles, all_labels, loc='upper right', bbox_to_anchor=(0.9, ypos), ncol=2, frameon=True, bbox_transform=fig.transFigure)
		
	def add_meta_info(self, title=None, ylabel=None, xlabel=None, ts=13, ls=11):
		"""
		Add meta info to the figure.
		
		Parameters
		----------
		title: str
			- Title of the figure.
			- Default: None
		ylabel: str
			- y label of the signal.
			- It will only appear in the signal subplot.
			- Default: None
		xlabel: str
			- x label of the signal.
			- It will only appear in the signal subplot.
			- Default: None
		ts: Number
			- Title size
			- Default: 10
		ls: Number
			- Label size.
			- Default: 10
		
		Returns
		-------
		None
		"""
		subplots: list = self._subplots
		fig = self._fig
		
		ref_subplot = subplots[0]
		signal_subplot = subplots[-1]
		
		if title is not None:
			ref_subplot.set_title(title, pad=10, size=ts)
		if ylabel is not None:
			signal_subplot.set_ylabel(ylabel, size=ls)
		if xlabel is not None:
			signal_subplot.set_xlabel(xlabel, size=ls)
		
	def save(self, path="./figure.png"):
		"""
		Save the figure.

		Parameters
		----------
		path: str
			- Path to the output file.

		Returns
		-------
		None
		"""
		fig = self._fig
		fig.savefig(path, bbox_inches="tight")
		


#======== Plot distribution ===========
def plot_dist(*args, ann=None, xlim=None, ylim=None, ylabel=None, xlabel=None, title=None, legend=None, show_hist=True, npoints=200, bins=30):
		"""
		Plot distribution.

		.. code-block:: python
			
			import modusa as ms
			import numpy as np
			np.random.seed(42)
			data = np.random.normal(loc=1, scale=1, size=1000)
			ms.plot_dist(data, data+5, data-10, ann=[(0, 1, "A")], legend=("D1", "D2", "D3"), ylim=(0, 1), xlabel="X", ylabel="Counts", title="Distribution")

		Parameters
		----------
		*args: ndarray
			- Data arrays for which distribution needs to be plotted.
			- Arrays will be flattened.
		ann : list[tuple[Number, Number, str] | None
			- A list of annotations to mark specific points. Each tuple should be of the form (start, end, label).
			- Default: None => No annotation.
		events : list[Number] | None
			- A list of x-values where vertical lines (event markers) will be drawn.
			- Default: None
		xlim : tuple[Number, Number] | None
			- Limits for the x-axis as (xmin, xmax).
			- Default: None
		ylim : tuple[Number, Number] | None
			- Limits for the y-axis as (ymin, ymax).
			- Default: None
		xlabel : str | None
			- Label for the x-axis.
			- - Default: None
		ylabel : str | None
			- Label for the y-axis.
			- Default: None
		title : str | None
			- Title of the plot.
			- Default: None
		legend : list[str] | None
			- List of legend labels corresponding to each signal if plotting multiple distributions.
			- Default: None
		show_hist: bool
			- Want to show histogram as well.
		npoints: int
			- Number of points for which gaussian needs to be computed between min and max.
			- Higher value means more points are evaluated with the fitted gaussian, thereby higher resolution.
		bins: int
			- The number of bins for histogram.
			- This is used only to plot the histogram.

		Returns
		-------
		plt.Figure
			- Matplotlib figure.
		"""
		from scipy.stats import gaussian_kde
	
		if isinstance(legend, str):
			legend = (legend, )
			
		if legend is not None:
			if len(legend) < len(args):
				raise ValueError(f"Legend should be provided for each signal.")
				
		# Create figure
		fig = plt.figure(figsize=(16, 4))
		gs = gridspec.GridSpec(2, 1, height_ratios=[0.1, 1])
	
		colors = plt.get_cmap('tab10').colors
	
		dist_ax = fig.add_subplot(gs[1, 0])
		annotation_ax = fig.add_subplot(gs[0, 0], sharex=dist_ax)
	
		# Set limits
		if xlim is not None:
			dist_ax.set_xlim(xlim)
			
		if ylim is not None:
			dist_ax.set_ylim(ylim)
			
		# Add plot
		for i, data in enumerate(args):
			# Fit gaussian to the data
			kde = gaussian_kde(data)
			
			# Create points to evaluate KDE
			x = np.linspace(np.min(data), np.max(data), npoints)
			y = kde(x)
			
			if legend is not None:
				dist_ax.plot(x, y, color=colors[i], label=legend[i])
				if show_hist is True:
					dist_ax.hist(data, bins=bins, density=True, alpha=0.3, facecolor=colors[i], edgecolor='black', label=legend[i])
			else:
				dist_ax.plot(x, y, color=colors[i])
				if show_hist is True:
					dist_ax.hist(data, bins=bins, density=True, alpha=0.3, facecolor=colors[i], edgecolor='black')
					
		# Add annotations
		if ann is not None:
			annotation_ax.set_ylim(0, 1) # For consistent layout
			# Determine visible x-range
			x_view_min = xlim[0] if xlim is not None else np.min(x)
			x_view_max = xlim[1] if xlim is not None else np.max(x)
			for i, (start, end, tag) in enumerate(ann):
				# We make sure that we only plot annotation that are within the x range of the current view
				if start >= x_view_max or end <= x_view_min:
					continue
				
				# Clip boundaries to xlim
				start = max(start, x_view_min)
				end = min(end, x_view_max)
				
				color = colors[i % len(colors)]
				width = end - start
				rect = Rectangle((start, 0), width, 1, color=color, alpha=0.7)
				annotation_ax.add_patch(rect)
				
				text_obj = annotation_ax.text((start + end) / 2, 0.5, tag, ha='center', va='center', fontsize=10, color='white', fontweight='bold', zorder=10, clip_on=True)
				text_obj.set_clip_path(rect)
				
		# Add legend
		if legend is not None:
			handles, labels = dist_ax.get_legend_handles_labels()
			fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(0.9, 1.1), ncol=len(legend), frameon=True)
			
		# Set title, labels
		if title is not None:
			annotation_ax.set_title(title, pad=10, size=11)
		if xlabel is not None:
			dist_ax.set_xlabel(xlabel)
		if ylabel is not None:
			dist_ax.set_ylabel(ylabel)
			
		# Remove the boundaries and ticks from annotation axis
		if ann is not None:
			annotation_ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
		else:
			annotation_ax.axis("off")
			
		fig.subplots_adjust(hspace=0.01, wspace=0.05)
		plt.close()
		return fig