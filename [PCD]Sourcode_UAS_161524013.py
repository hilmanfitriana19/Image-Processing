from tkinter import Label,Button,Frame,filedialog,simpledialog,messagebox,ttk
from tkinter.ttk import Treeview
from tkinter import *
import cv2
from PIL import Image,ImageTk
import numpy
import random
import math

class window(Frame):
    def __init__(self, master=None):
        self.frame=Frame.__init__(self,master)   
        self.master=master  
        self.initwindow(self.frame)        
    #inisiasi frame
    def initwindow(self,master):
        self.master.title("UAS PENGOLAHAN CITRA DIGITAL HILMAN")
        self.master.geometry("1350x670+0+0")                                    #ukuran size 1350 x 570 posisi awal di 0,0
        self.master.minsize(1350,670)                                           #ukuran terkecil (tidak bisa diperkecil lagi)
        self.initmenu(master)
        self.left_window(master)        
        self.right_window(master)      
        self.array=[]
    #pembuatan menu pada frame
    def initmenu(self,master):
        self.menubar = Menu(master)                                                          
        self.filemenu = Menu(self.menubar, tearoff=0)                                           #tearoff = menghilangkan garis putus-putus
        self.filemenu.add_command(label="Browse Gambar",command=self.openimage)
        self.filemenu.add_command(label="Simpan Hasil Proses",command=self.saveimage,state="disable")        
        self.menubar.add_cascade(label="File", menu=self.filemenu)                              #menambahkan file menu ke menubar

        warna = Menu(self.menubar, tearoff=0)        
        warna.add_command(label="Grayscale",command=self.grayscale)
        warna.add_command(label="Black&White",command=self.blackwhite)
        warna.add_separator()                                                                           #tambah garis pemisah
        warna.add_command(label="Brightening",command=lambda : self.brigness_darkening("brightening"))
        warna.add_command(label="Darkening",command=lambda : self.brigness_darkening("darkening"))              #lambda biar henteu langsung di run commandna        
        self.menubar.add_cascade(label="Warna",menu=warna,state="disable")                              # default menu disabled

        morfology = Menu(self.menubar, tearoff=0)
        morfology.add_command(label="Erosi",command=lambda : self.morphology("erosi"))
        morfology.add_command(label="Dilasi",command=lambda : self.morphology("dilasi"))
        morfology.add_command(label="Opening",command=lambda : self.morphology("opening"))
        morfology.add_command(label="Closing",command=lambda : self.morphology("closing"))     
        self.menubar.add_cascade(label="Morfology",menu=morfology,state="disable")                                            

        filtering = Menu(self.menubar,tearoff=0)
        filtering.add_command(label="Mean Filtering",command=lambda : self.filtering("mean"))
        filtering.add_command(label="Median Filtering",command=lambda : self.filtering("median"))
        filtering.add_command(label="Gaussian Filtering",command=lambda : self.filtering("gaussian"))
        self.menubar.add_cascade(label="Filtering",menu=filtering,state="disable")                        
                                               
        edge_detection=Menu(self.menubar,tearoff=0)
        edge_detection.add_command(label="Roberts",command=lambda : self.edge_detection("robert"))
        edge_detection.add_command(label="Prewitt",command=lambda : self.edge_detection("prewitt"))
        edge_detection.add_command(label="Sobel",command=lambda : self.edge_detection("sobel"))        
        edge_detection.add_command(label="Canny",command=lambda : self.edge_detection("canny"))
        edge_detection.add_command(label="Laplacian",command=lambda : self.edge_detection("laplacian"))
        self.menubar.add_cascade(label="Deteksi Garis",menu=edge_detection,state="disable")               

        noise=Menu(self.menubar,tearoff=0)
        noise.add_command(label="Salt & pepper",command=self.salt_pepper)        
        self.menubar.add_cascade(label="Tambah Noise",menu=noise,state="disable")               

        self.psnr=Menu(self.menubar,tearoff=0)
        self.psnr.add_command(label="Hitung PSNR",command=self.hitung_psnr)        
        self.psnr.add_command(label="Lihat Tabel PSNR",state="disable",command=self.show_psnr)        
        self.menubar.add_cascade(label="PSNR",menu=self.psnr,state="disable")

        self.master.config(menu=self.menubar)                                # mengatur menu utama dengan menubar
        
        Label(master, text="Proses Pengolahan Citra",pady=20,font=("Times New Roman",19)).grid(column=1)     #.grid ditampilkan pada colom 1 row 0

    #inisiasi citra awal (kiri)
    def left_window(self,master):        
        Label(master, text="Gambar Asli",pady=10,font=("Times New Roman",16,"bold"),height=1).grid(column=0,row=1,sticky=W+E)        
        self.left_gambar = Label(master, text="Gambar Kosong",width=78,height=37,relief=GROOVE)         #set width (caracter length)
        self.left_gambar.grid(row=3)          
    
    #inisiasi label citra hasil pengolahan (kanan)
    def right_window(self,master):         
        Label(master, text="Gambar Hasil Pemrosesan",pady=10,font=("Times New Roman",16,"bold"),height=1).grid(column=2,row=1,sticky=W+E)                        
        self.right_gambar = Label(master, text="Gambar Kosong",width=78,height=37,relief=GROOVE)        
        self.right_gambar.grid(row=3,column=2)        

    #menampilkan citra hasil pengolahan
    def set_right_gambar(self,hasil):              
        if self.filemenu.entrycget(1,"state")=="disabled":                #enable menu "Simpan Gambar Hasil" ketika citra di bagian kanan sudah muncul
            self.filemenu.entryconfig("Simpan Hasil Proses",state="normal")                        
            self.psnr.entryconfig("Lihat Tabel PSNR",state="normal")
        hasil=Image.fromarray(hasil)                      #array to image       
        self.proses=hasil
        hasil = hasil.resize((550,550),Image.ANTIALIAS)                 #resize gambar ukuran 550x550            
        hasil=ImageTk.PhotoImage(hasil)   
        self.right_gambar.__setitem__("image",hasil)                    #set value image
        self.right_gambar.image=hasil                
        if self.right_gambar.__getitem__("text")=="Gambar Kosong" :     #ubah ukuran label dari character width jadi pixel
            self.right_gambar.__setitem__("width",550)                  #set width (pixel)
            self.right_gambar.__setitem__("height",550)
            self.right_gambar.__setitem__("text","")                    # kosongkan text

    #manipulasi citra (RGB2GRAYSCALE)
    def grayscale(self):            
        hasil=numpy.array(self.proses)                       #image ke array
        hasil=cv2.cvtColor(hasil,cv2.COLOR_BGR2GRAY)        #format image dalam BGR bukan RGB
        self.right_image=hasil   
        self.set_right_gambar(hasil)        

    #manipulasi citra (RGB2BINER)
    def blackwhite(self):                                 
        hasil=numpy.array(self.proses)                    
        hasil=cv2.cvtColor(hasil,cv2.COLOR_BGR2GRAY)
        ret,hasil=cv2.threshold(hasil,127,255,cv2.THRESH_BINARY)          
        self.right_image=hasil
        self.set_right_gambar(hasil)  

    #load citra
    def openimage(self):
        self.src = filedialog.askopenfilename()                      #openfile
        if len(self.src)>0:                                                    
            self.original =Image.open(self.src)
            self.proses=self.original.resize((550,550),Image.ANTIALIAS)            
            hasil = self.proses
            hasil = ImageTk.PhotoImage(hasil)            
            if self.left_gambar.__getitem__("text")=="Gambar Kosong":               #atur ukuran label menjadi ukuran gambar (pixel)
                self.left_gambar.__setitem__("width",550)
                self.left_gambar.__setitem__("height",550)
                self.left_gambar.__setitem__("text","")                          
            self.left_gambar.__setitem__("image",hasil)                            #tampilkan gambar ke label kiri
            self.left_gambar.image = hasil                                         #menjaga referensi (menghindari garbage collection)
            if self.menubar.entrycget(2,"state")=="disabled":                      #mengaktifkan menu yang disable sebelumnya
                self.menubar.entryconfig("Deteksi Garis",state="normal")
                self.menubar.entryconfig("Filtering",state="normal")
                self.menubar.entryconfig("Morfology",state="normal")
                self.menubar.entryconfig("Warna",state="normal")            
                self.menubar.entryconfig("Tambah Noise",state="normal")            
                self.menubar.entryconfig("PSNR",state="normal")            

    #edge detection canny

    def edge_detection(self,jenis):
        hasil=numpy.array(self.proses)                    
        hasil=cv2.cvtColor(hasil,cv2.COLOR_BGR2GRAY)        
        hasil = cv2.GaussianBlur(hasil, (5, 5), 0)  #blurring (gaussian filter)
        if jenis == "canny" :
            hasil = cv2.Canny(hasil, self.input_value("Nilai Threshold", "Batas Threshold Bawah"), self.input_value("Nilai Threshold", "Batas Threshold Atas"))                
        elif jenis == "sobel":
            img_sobelx = cv2.Sobel(hasil,cv2.CV_8U,1,0,ksize=3)                
            img_sobely = cv2.Sobel(hasil,cv2.CV_8U,0,1,ksize=3)
            hasil = img_sobelx + img_sobely                     #menggabungkan hasil sobel vertical + horizontal
        elif jenis =="robert":
            kernelx = numpy.array([[-1,0],[0,1]])
            kernely = numpy.array([[0,-1],[1,0]])
            img_robertx = cv2.filter2D(hasil, -1, kernelx)
            img_roberty = cv2.filter2D(hasil, -1, kernely)        
            hasil = img_robertx+img_roberty
        elif jenis =="prewitt":
            kernelx = numpy.array([[1,1,1],[0,0,0],[-1,-1,-1]])
            kernely = numpy.array([[-1,0,1],[-1,0,1],[-1,0,1]])
            img_prewittx = cv2.filter2D(hasil, -1, kernelx)
            img_prewitty = cv2.filter2D(hasil, -1, kernely)        
            hasil = img_prewittx+img_prewitty        
        elif jenis =="laplacian":
            hasil =cv2.Laplacian(hasil,cv2.CV_64F,3)            
        self.right_image=hasil                  # self.right_image untuk penyimpanan file hasil, tidak menggunakan hasil karena kalo berwarna format yang harus disimpan BGR
        self.set_right_gambar(hasil)            #deteksi garis dalam GRAYSCALE tidak usah di ke BGR kan

    #simpan citra hasil pengolahan  (kanan)
    def saveimage(self):                      
        path=filedialog.asksaveasfilename(defaultextension=".png")                  #simpan extensi png   
        if path != "":            
            cv2.imwrite(path,self.right_image)                                     

    #manipulasi citra morpology
    def morphology(self,bentuk):
        hasil=self.proses.convert('RGB')   
        hasil=numpy.array(hasil)       
        kernel = self.input_kernel("Pemilihan Ukuran Kernel","Ukuran Kernel ?")  
        if bentuk == "erosi":
            hasil = cv2.erode(hasil,kernel,iterations = 1)
        elif bentuk == "dilasi":
            hasil = cv2.dilate(hasil,kernel,iterations = 1)
        elif bentuk == "opening":
            hasil = cv2.morphologyEx(hasil, cv2.MORPH_OPEN, kernel)
        elif bentuk == "closing":
            hasil = cv2.morphologyEx(hasil, cv2.MORPH_CLOSE, kernel)        
        self.right_image=cv2.cvtColor(hasil,cv2.COLOR_RGB2BGR)        
        self.set_right_gambar(hasil) 

    #manipulasi citra filtering
    def filtering(self,bentuk):
        hasil=self.proses.convert('RGB')   
        hasil=numpy.array(hasil)      
        koefisien = self.input_value("Pemilihan Kernel","Ukuran Kernel")           
        if bentuk == "mean" :        
            hasil = cv2.blur(hasil,(koefisien,koefisien))
        elif bentuk =="gaussian":
            hasil = cv2.GaussianBlur(hasil,(koefisien,koefisien),0)
        elif bentuk =="median":
            hasil = cv2.medianBlur(hasil,koefisien)
        self.right_image=cv2.cvtColor(hasil,cv2.COLOR_RGB2BGR)        
        self.set_right_gambar(hasil) 
    
    def input_kernel(self,judul,pesan):                
        answer=self.input_value(judul,pesan)
        if answer != 0:
            answer = numpy.ones((answer,answer),numpy.uint8)                # matriks nxn semua elemen 1
        else:
            answer = numpy.ones((1,1),numpy.uint8)                            
        return answer
    
    def input_value(self,nama_window,pesan):        
        answer = simpledialog.askinteger(nama_window,pesan,minvalue=0, maxvalue=255,initialvalue=0)        
        if answer is None:                    
            answer = 0
        return answer

    #manipulasi citra brigness darkening
    def brigness_darkening(self,param):
        hasil=self.proses.convert('RGB')                     #jikapun citra dalam bentuk grayscale, tetap dibaca sebagai BGR
        hasil=numpy.array(hasil)                 
        koefisien = self.input_value("Pemilihan Konstanta","Nilai Konstanta") 
        if koefisien != 0 :        
            for r in range(len(hasil)):
                for s in range(len(hasil[r])):
                    if param == "brightening":               
                        hasil[r][s][0] = numpy.clip(hasil[r][s][0] + koefisien, 0, 255)  #numpy.clip prinsip conservative filtering
                        hasil[r][s][1] = numpy.clip(hasil[r][s][1] + koefisien, 0, 255)
                        hasil[r][s][2] = numpy.clip(hasil[r][s][2] + koefisien, 0, 255)                                       
                    else :
                        hasil[r][s][0] = numpy.clip(hasil[r][s][0] - koefisien, 0, 255)
                        hasil[r][s][1] = numpy.clip(hasil[r][s][1] - koefisien, 0, 255)
                        hasil[r][s][2] = numpy.clip(hasil[r][s][2] - koefisien, 0, 255)                                       
            self.right_image=cv2.cvtColor(hasil,cv2.COLOR_RGB2BGR)                
            self.set_right_gambar(hasil)              
    
    def salt_pepper(self):
        hasil=self.proses.convert('RGB')                     #jikapun citra dalam bentuk grayscale, tetap dibaca sebagai BGR
        hasil=numpy.array(hasil)                 
        intensitas = simpledialog.askfloat("Nilai Intesitas Noise","Intensitas Noise",minvalue=0, maxvalue=1,initialvalue=0)        
        if intensitas is None:                    
            intensitas = 0
        intensitas*=0.5
        thres = 1 - intensitas                      
        for i in range(hasil.shape[0]):
            for j in range(hasil.shape[1]):
                rdn = random.random()
                if rdn < intensitas:
                    hasil[i][j][0]=0
                    hasil[i][j][1]=0
                    hasil[i][j][2]=0
                elif rdn > thres:
                    hasil[i][j][0]=255
                    hasil[i][j][1]=255
                    hasil[i][j][2]=255                
        self.right_image=cv2.cvtColor(hasil,cv2.COLOR_RGB2BGR)                
        self.set_right_gambar(hasil)  
        
    def show_psnr(self):                
        top = Toplevel(width=300,height=300)
        top.title("Nilai MSE dan PSNR")
        top.minsize(300,300)
        tree = Treeview(top, columns=('MSE', 'PSNR'))    
        tree.heading('#0', text='File')
        tree.heading('#1', text='MSE')
        tree.heading('#2', text='PSNR (db)')    
        tree.column('#0',anchor='center',width=200,stretch="true")
        tree.column('#1',anchor='center',width=100,stretch="true")
        tree.column('#2',anchor='center',width=200,stretch="true")
        
        for i in self.array :
            tree.insert('', 'end', text=i[0], values=(i[1], i[2]))                
        tree.grid(padx=10,pady=10)
        close = Button(top,text="Close",pady=10,command=top.destroy,relief="groove",width=10)        
        close.grid(row=1,sticky="E",padx=10,pady=10)

        top.mainloop()
        

    def hitung_psnr(self):                
        proses = self.proses.resize((550,550),Image.ANTIALIAS)            
        original = self.original.resize((550,550),Image.ANTIALIAS)            
        original=numpy.array(original)                    
        proses=numpy.array(proses)                    
        original=cv2.cvtColor(original,cv2.COLOR_BGR2GRAY)     
        proses=cv2.cvtColor(proses,cv2.COLOR_BGR2GRAY)                     
        mse = numpy.mean(numpy.subtract(original,proses)**2)        
        if mse == 0:            
            nilai_psnr="tak hingga"
        else : 
            nilai_psnr=20 * math.log10(255.0 / math.sqrt(mse))
        self.array.append([self.src.split("/")[-1],mse,nilai_psnr])        
        self.show_psnr()
    
root = Tk()
my_gui = window(root)
root.mainloop()
