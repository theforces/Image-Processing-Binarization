import wx
import numpy as np

class BinaryApp(wx.App):

	def __init__(self, redirect = False):
		#create the application object
		wx.App.__init__(self, redirect)

		#create a window
		self.frame = wx.Frame(None, title = "Image Processing - Binarization", style = wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX) & (~wx.RESIZE_BORDER))

		#create a panel encompassing all widgets
		#insert the panel into frame
		self.panel = wx.Panel(self.frame)

		self.imgMaxSize = 512
		self.imgDefaultSize = 256
		self.thresholdDefaultValue = 127
		self.thresholdCurrentValue = self.thresholdDefaultValue

		self.imageLoaded = False

		#create the widgets for the panel
		self.createWidgets()

		#show the frame
		self.frame.Show()

	def createWidgets(self):

		#create image object
		self.originalImg = wx.Image(self.imgDefaultSize, self.imgDefaultSize)

		#create image controls for the actual image data
		self.originalImgCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(self.originalImg))

		self.grayImg = wx.Image(self.imgDefaultSize, self.imgDefaultSize)
		self.grayImgCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(self.grayImg))

		self.binaryImg = wx.Image(self.imgDefaultSize, self.imgDefaultSize)
		self.binaryImgCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(self.binaryImg))

		self.originalImgPath = ""

		#create the browse button
		self.browseBtn = wx.Button(self.panel, label = "Browse")
		self.browseBtn.Bind(wx.EVT_BUTTON, self.onBrowse)
		self.browseBtn.SetToolTip(wx.ToolTip("Open an image"))

		#create the threshold slider
		self.thresholdSlider = wx.Slider(self.panel, value = self.thresholdDefaultValue, minValue = 0, maxValue = 255, style = wx.SL_HORIZONTAL|wx.SL_LABELS)
		self.thresholdSlider.Bind(wx.EVT_SLIDER, self.onSliderScroll)

		#create subwindows for organizing the layout
		#the main subwindow is used for organizing the following 3 subwindows horizontally
		#the other 3 subwindows are used for showing information about each image
		self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.originalImgSizer = wx.BoxSizer(wx.VERTICAL)
		self.grayImgSizer = wx.BoxSizer(wx.VERTICAL)
		self.binaryImgSizer = wx.BoxSizer(wx.VERTICAL)

		self.originalImgSizer.Add(wx.StaticText(self.panel, label = 'Original image'), 0, wx.ALL, 5)
		self.originalImgSizer.Add(self.originalImgCtrl, 0, wx.ALL, 5)
		self.originalImgSizer.Add(self.browseBtn, 0, wx.ALL, 5)

		self.grayImgSizer.Add(wx.StaticText(self.panel, label = 'Grayscale image'), 0, wx.ALL, 5)
		self.grayImgSizer.Add(self.grayImgCtrl, 0, wx.ALL, 5)

		self.binaryImgSizer.Add(wx.StaticText(self.panel, label = 'Binary image'), 0, wx.ALL, 5)
		self.binaryImgSizer.Add(self.binaryImgCtrl, 0, wx.ALL, 5)
		self.binaryImgSizer.Add(wx.StaticText(self.panel, label = 'Threshold value'), 0, wx.ALL, 5)
		self.binaryImgSizer.Add(self.thresholdSlider, 1, flag = wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border = 5)

		self.mainSizer.Add(self.originalImgSizer, 0, wx.ALL, 5)
		self.mainSizer.Add(self.grayImgSizer, 0, wx.ALL, 5)
		self.mainSizer.Add(self.binaryImgSizer, 0, wx.ALL, 5)

		#set the main sizer
		self.panel.SetSizer(self.mainSizer)

		#fit the sizer contents into the frame
		self.mainSizer.Fit(self.frame)

		#lay out the children of this window using the main sizer
		self.panel.Layout()

	#browse for and open an image
	def onBrowse(self, event):
		#open a file dialog and choose an image
		dialog = wx.FileDialog(None, "Choose an image", wildcard = "JPG files (*.jpeg, *.jpg)|*.jpeg;*.jpg|PNG files (*.png)|*.png|BMP files (*.bmp)|*.bmp", style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if dialog.ShowModal() == wx.ID_OK:
			self.originalImgPath = dialog.GetPath()
			self.onImageLoad()
		dialog.Destroy()

	#when the threshold slider is scrolled
	def onSliderScroll(self, event):
		if self.imageLoaded:
			self.thresholdCurrentValue = self.thresholdSlider.GetValue()

			self.binaryImg = self.gray2bin(self.grayImg.Copy(), self.thresholdCurrentValue)
			self.binaryImgCtrl.SetBitmap(wx.Bitmap(self.binaryImg))

	#image manipulation
	def onImageLoad(self):
		#load the image
		img = wx.Image(self.originalImgPath, wx.BITMAP_TYPE_ANY)
		self.imageLoaded = True

		w = img.GetWidth()
		h = img.GetHeight()

		#resizing the image so it can fit in the window
		if w > h:
			newW = self.imgMaxSize
			newH = self.imgMaxSize * h / w
		else:
			newH = self.imgMaxSize
			newW = self.imgMaxSize * w / h

		img = img.Scale(int(newW), int(newH))

		#set the new images
		self.originalImg = img
		self.grayImg = img.ConvertToGreyscale()
		self.binaryImg = self.gray2bin(self.grayImg.Copy(), self.thresholdCurrentValue)

		#reload the image controls
		self.originalImgCtrl.SetBitmap(wx.Bitmap(self.originalImg))
		self.grayImgCtrl.SetBitmap(wx.Bitmap(self.grayImg))
		self.binaryImgCtrl.SetBitmap(wx.Bitmap(self.binaryImg))

		#refresh the panel to see the changes
		self.panel.Refresh()

		#fit the new content into the frame
		self.mainSizer.Fit(self.frame)

	def gray2bin(self, image, threshold = 127):
		#get image data buffer
		buf = image.GetDataBuffer()

		#transform buffer into a numpy array
		arr = np.frombuffer(buf, dtype = 'uint8')

		#binary array starts with zeros
		bin = np.zeros(len(arr), dtype = 'uint8')

		#fill the binary array with 255 where the numpy array values are bigger than the threshold 
		bin[np.asarray(np.where(arr > threshold))] = 255

		#set image data to a string representation of the binary array
		image.SetData(bin.tostring())
		return image

if __name__ == "__main__":
	#main loop program
	app = BinaryApp()
	app.MainLoop()
