
import tkinter as tk

class ToolTip():
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None 

    def show_tip(self, tip_text):
        
        # Display text in a tooltip window
        
        if self.tip_window or not tip_text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")  # get size of widget
        x = x = self.widget.winfo_rootx() + 25      # calculate to display tooltip
        y = y + cy + self.widget.winfo_rooty() + 25 # below and to the right
        self.tip_window = tw = tk.Toplevel(self.widget) # create new tip window
        tw.wm_overrideredirect(True)             # remove window manager decorations
        #tw.wm_overrideredirect(False)  # uncomment to see effect
        tw.wm_geometry("+%d+%d" % (x, y))   # create window size

        label = tk.Label(tw, text=tip_text, justify=tk.LEFT,
            background="#ffffe0", relief=tk.SOLID, borderwidth=1,
            font=("tahome", "8", "normal"))
        label.configure(foreground = 'black')
        label.pack(ipadx=1)
        self.tip_window.after(2500, self.tip_window.destroy)

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

def create_ToolTip(widget, text):
    toolTip = ToolTip(widget)      # Create instance of class
    def enter(event):
        toolTip.show_tip(text)
    def leave(event):
        toolTip.hide_tip()
    widget.bind('<Enter>', enter)  # Bind mouse events
    widget.bind('<Leave>', leave)
    