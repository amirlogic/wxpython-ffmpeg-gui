import wx
import subprocess
import os
import threading

class FFMPEGCheckerFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='FFMPEG GUI', size=(800, 600))
        panel = wx.Panel(self)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        menubar = wx.MenuBar()

        file_menu = wx.Menu()
        open_item = file_menu.Append(wx.ID_OPEN, '&Open\tCtrl+O', 'Open a file to convert')
        self.Bind(wx.EVT_MENU, self.on_select_file, open_item)
        menubar.Append(file_menu, '&File')

        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, '&About', 'About this program')
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        menubar.Append(help_menu, '&Help')

        self.SetMenuBar(menubar)

        # Increased top padding for clear separation from the menu
        main_sizer.AddSpacer(50)

        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)

        format_label = wx.StaticText(panel, label='Select Target Format:')

        format_label.SetPosition((20, 34))

        controls_sizer.Add(format_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)

        

        self.format_choice = wx.ComboBox(panel, choices=['mp4', 'avi', 'mkv', 'mov'], style=wx.CB_READONLY)
        
        self.format_choice.SetPosition((150, 30))

        self.format_choice.SetSelection(0)
        controls_sizer.Add(self.format_choice, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)


        

        self.convert_button = wx.Button(panel, label='Convert')

        self.convert_button.SetPosition((250, 30))

        self.convert_button.Bind(wx.EVT_BUTTON, self.on_convert)
        controls_sizer.Add(self.convert_button, flag=wx.ALIGN_CENTER_VERTICAL)

        main_sizer.Add(controls_sizer, flag=wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border=20)

        # Ensure the text area is placed below without overlap, with fixed size
        self.output_ctrl = wx.TextCtrl(panel, size=(750, 400), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.VSCROLL)

        self.output_ctrl.SetPosition((20, 100))

        main_sizer.Add(self.output_ctrl, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP, border=20)

        panel.SetSizer(main_sizer)

        self.selected_file = None

        self.Centre()
        self.Show()

        wx.CallLater(100, self.check_ffmpeg_version)

    def check_ffmpeg_version(self):
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
            self.output_ctrl.SetValue(f"{result.stdout}\nPlease select a file to convert...\n")
        except subprocess.CalledProcessError as e:
            self.output_ctrl.SetValue("FFMPEG returned an error:\n" + e.stderr)
        except FileNotFoundError:
            self.output_ctrl.SetValue("FFMPEG is not installed or not found in PATH.")

    def on_select_file(self, event):
        with wx.FileDialog(self, "Select file to convert", wildcard="Video files (*.mp4;*.avi;*.mkv;*.mov)|*.mp4;*.avi;*.mkv;*.mov|All files (*.*)|*.*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.selected_file = fileDialog.GetPath()
            self.output_ctrl.AppendText(f"\nSelected file: {self.selected_file}\n")

    def on_convert(self, event):
        if not self.selected_file:
            self.output_ctrl.AppendText("No file selected for conversion.\n")
            return
        target_format = self.format_choice.GetValue()
        output_file = os.path.splitext(self.selected_file)[0] + f"_converted.{target_format}"

        self.convert_button.Disable()
        self.format_choice.Disable()

        processing_dialog = wx.ProgressDialog("Processing", "Conversion in progress...", parent=self, style=wx.PD_APP_MODAL)  # | wx.PD_ELAPSED_TIME

        def conversion_task():
            try:
                result = subprocess.run(['ffmpeg', '-i', self.selected_file, output_file], capture_output=True, text=True)
                wx.CallAfter(processing_dialog.Destroy)
                if result.returncode == 0:
                    wx.CallAfter(self.output_ctrl.AppendText, f"Conversion completed successfully.\nOutput file saved at: {output_file}\nAnother file to convert?\n")
                else:
                    wx.CallAfter(self.output_ctrl.AppendText, f"Conversion failed:\n{result.stderr}\nExpected output file: {output_file}\n")
            except Exception as e:
                wx.CallAfter(processing_dialog.Destroy)
                wx.CallAfter(self.output_ctrl.AppendText, f"Error during conversion: {e}\nExpected output file: {output_file}\n")
            finally:
                wx.CallAfter(self.convert_button.Enable)
                wx.CallAfter(self.format_choice.Enable)

        threading.Thread(target=conversion_task).start()

    def on_about(self, event):

       wx.MessageBox("FFMPEG GUI\nVersion: Alpha\n\nThis program allows you to check FFMPEG availability and convert videos to different formats using a simple GUI.\n\n(C) 2025 Amir Hachaichi <admin@synlaunch.com>",
                     "About FFMPEG GUI", wx.OK | wx.ICON_INFORMATION)

if __name__ == '__main__':
    app = wx.App(False)
    frame = FFMPEGCheckerFrame()
    app.MainLoop()
