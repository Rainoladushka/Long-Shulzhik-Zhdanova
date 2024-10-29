import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import messagebox

class Quaternion:
    def __init__(self, a, b, c, d):
        self.a = a  # Real part
        self.b = b  # Imaginary part i
        self.c = c  # Imaginary part j
        self.d = d  # Imaginary part k
    
    # Addition
    def add_Quaternion(self, other):             
        return Quaternion(self.a + other.a,     
                          self.b + other.b,     
                          self.c + other.c,     
                          self.d + other.d)     

    # Multiplication
    def multiply_Quaternion(self, other):            
        a1, b1, c1, d1 = self.a, self.b, self.c, self.d
        a2, b2, c2, d2 = other.a, other.b, other.c, other.d
        
        return Quaternion(
            a1*a2 - b1*b2 - c1*c2 - d1*d2,  # Real part
            a1*b2 + b1*a2 + c1*d2 - d1*c2,  # Imaginary part i
            a1*c2 - b1*d2 + c1*a2 + d1*b2,  # Imaginary part j
            a1*d2 + b1*c2 - c1*b2 + d1*a2   # Imaginary part k
        )

    # # Conjugation
    def conjugate_Quaternion(self):         
        return Quaternion(self.a, -self.b, -self.c, -self.d)

    # norm
    def norm_Quaternion(self):
        return math.sqrt(self.a**2 + self.b**2 + self.c**2 + self.d**2)

    # Inverse
    def inverse_Quaternion(self):
        norm_sq = self.norm_Quaternion()**2
        if norm_sq == 0:
            raise ZeroDivisionError("Cannot invert a quaternion with zero norm.")
        conjugate = self.conjugate_Quaternion()
        return Quaternion(conjugate.a / norm_sq, 
                          conjugate.b / norm_sq, 
                          conjugate.c / norm_sq, 
                          conjugate.d / norm_sq)

    # Rotate vectors (x, y, z) via quaternions
    def rotate_vector(self, vector):
        vec_quat = Quaternion(0, *vector)  # Convert vector to quaternion
        rotated = self.multiply_Quaternion(vec_quat).multiply_Quaternion(self.inverse_Quaternion())  # rotation process
        return (rotated.b, rotated.c, rotated.d)  # Returns the rotation vector

# 3D animation drawing function
def plot_quaternion_rotation(q, vector):
    # Create a grid of points for the axis
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Draw initial vector
    ax.quiver(0, 0, 0, vector[0], vector[1], vector[2], color='b', label='Initial vector', arrow_length_ratio=0.1)

    # Rotate vectors and draw rotation vectors
    rotated_vector = q.rotate_vector(vector)
    ax.quiver(0, 0, 0, rotated_vector[0], rotated_vector[1], rotated_vector[2], color='r', label='Rotation vector', arrow_length_ratio=0.1)

    # Set properties for the graph
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Rotate Vector through Quadratices')
    ax.legend()
    plt.show()

# Function to handle addition
def add_quaternions():
    try:
        a1 = float(entry_a1.get())
        b1 = float(entry_b1.get())
        c1 = float(entry_c1.get())
        d1 = float(entry_d1.get())

        a2 = float(entry_a2.get())
        b2 = float(entry_b2.get())
        c2 = float(entry_c2.get())
        d2 = float(entry_d2.get())

        q1 = Quaternion(a1, b1, c1, d1)
        q2 = Quaternion(a2, b2, c2, d2)
        q_sum = q1.add_Quaternion(q2)

        messagebox.showinfo("Result", f"Sum of 2 quaternions:\n{q_sum.a} + {q_sum.b}i + {q_sum.c}j + {q_sum.d}k")
    except ValueError:
        messagebox.showerror("Error", "Please enter full number!")
# multiplication processing function
def multiply_quaternions():
    try:
        a1 = float(entry_a1.get())
        b1 = float(entry_b1.get())
        c1 = float(entry_c1.get())
        d1 = float(entry_d1.get())

        a2 = float(entry_a2.get())
        b2 = float(entry_b2.get())
        c2 = float(entry_c2.get())
        d2 = float(entry_d2.get())

        q1 = Quaternion(a1, b1, c1, d1)
        q2 = Quaternion(a2, b2, c2, d2)
        q_multiply = q1.multiply_Quaternion(q2)

        messagebox.showinfo("Result", f"product of two quaternions:\n{q_multiply.a} + {q_multiply.b}i + {q_multiply.c}j + {q_multiply.d}k")
    except ValueError:
        messagebox.showerror("Error", "Please enter full number!")
#conjugate processing function
def conjugate_quaternions():
    try:
        a1 = float(entry_a1.get())
        b1 = float(entry_b1.get())
        c1 = float(entry_c1.get())
        d1 = float(entry_d1.get())

        q1 = Quaternion(a1, b1, c1, d1)
        q_conjugate = q1.conjugate_Quaternion()

        messagebox.showinfo("Result", f"conjunction of quaternions 1:\n{q_conjugate.a} + {q_conjugate.b}i + {q_conjugate.c}j + {q_conjugate.d}k")
    except ValueError:
        messagebox.showerror("Error", "Please enter full number!")
#quaternion norm processing function
def norm_quaternions():
    try:
        a1 = float(entry_a1.get())
        b1 = float(entry_b1.get())
        c1 = float(entry_c1.get())
        d1 = float(entry_d1.get())

        q1 = Quaternion(a1, b1, c1, d1)
        q_norm = q1.norm_Quaternion()
        messagebox.showinfo("Result", f"norm of quaternion 1:\n{q_norm}")
    except ValueError:
        messagebox.showerror("Error", "Please enter full number!")

#quaternion inverse function
def inverse_quaternions():
    try:
        a1 = float(entry_a1.get())
        b1 = float(entry_b1.get())
        c1 = float(entry_c1.get())
        d1 = float(entry_d1.get())

        q1 = Quaternion(a1, b1, c1, d1)
        q_inversion = q1.inverse_Quaternion()

        messagebox.showinfo("Result", f"inverse of quaternion 1:\n{q_inversion.a} + {q_inversion.b}i + {q_inversion.c}j + {q_inversion.d}k")
    except ValueError:
        messagebox.showerror("Error", "Please enter full number!")

# Function to handle rotation
def rotate_vector():
    try:
        a = float(entry_a.get())
        b = float(entry_b.get())
        c = float(entry_c.get())
        d = float(entry_d.get())

        q = Quaternion(a, b, c, d)

        vector = (1, 0, 0)  #input vector
        plot_quaternion_rotation(q, vector)
    except ValueError:
        messagebox.showerror("Error", "Please enter full number!")
# Function to reset all entries
def reset_entries():
    entry_a1.delete(0, tk.END)
    entry_b1.delete(0, tk.END)
    entry_c1.delete(0, tk.END)
    entry_d1.delete(0, tk.END)
    entry_a2.delete(0, tk.END)
    entry_b2.delete(0, tk.END)
    entry_c2.delete(0, tk.END)
    entry_d2.delete(0, tk.END)
    entry_a.delete(0, tk.END)
    entry_b.delete(0, tk.END)
    entry_c.delete(0, tk.END)
    entry_d.delete(0, tk.END)

# Interface settings
root = tk.Tk()
root.title("Quaternions Operations")

# Enter quaternion 1
tk.Label(root, text="quaternion 1 (a, b, c, d)").grid(row=0, column=0, columnspan=2)
entry_a1 = tk.Entry(root)
entry_a1.grid(row=1, column=0)
entry_b1 = tk.Entry(root)
entry_b1.grid(row=1, column=1)
entry_c1 = tk.Entry(root)
entry_c1.grid(row=1, column=2)
entry_d1 = tk.Entry(root)
entry_d1.grid(row=1, column=3)

# Enter quaternion 2
tk.Label(root, text="quaternion 2 (a, b, c, d)").grid(row=2, column=0, columnspan=2)
entry_a2 = tk.Entry(root)
entry_a2.grid(row=3, column=0)
entry_b2 = tk.Entry(root)
entry_b2.grid(row=3, column=1)
entry_c2 = tk.Entry(root)
entry_c2.grid(row=3, column=2)
entry_d2 = tk.Entry(root)
entry_d2.grid(row=3, column=3)

# btn_add
btn_add = tk.Button(root, text="Add quaternion", command=add_quaternions,width=16,height=2)
btn_add.grid(row=4, column=0)

#btn multiply 
btn_multiply = tk.Button(root, text="multiply quaternion", command=multiply_quaternions,width=16,height=2)
btn_multiply.grid(row=4, column=1)

#btn conjuigate
btn_conjuigate = tk.Button(root, text="conjuigate quaternion 1", command=conjugate_quaternions,width=16,height=2)
btn_conjuigate.grid(row=4, column=2)

#btn norm 
btn_norm = tk.Button(root, text="norm quaternion 1", command=norm_quaternions,width=16,height=2)
btn_norm.grid(row=5, column=0)

#btn inverse
btn_inverse=tk.Button(root, text="inverse quaternion 1", command=inverse_quaternions,width=16,height=2)
btn_inverse.grid(row=5, column=1)

# Button to reset all entries
btn_reset = tk.Button(root, text="Reset", command=reset_entries,width=16,height=2)
btn_reset.grid(row=5, column=2)
# Enter quaternion to rotate
tk.Label(root, text="Enter quaternion to rotate (a, b, c, d)").grid(row=6, column=0, columnspan=4)
entry_a = tk.Entry(root)
entry_a.grid(row=7, column=0)
entry_b = tk.Entry(root)
entry_b.grid(row=7, column=1)
entry_c = tk.Entry(root)
entry_c.grid(row=7, column=2)
entry_d = tk.Entry(root)
entry_d.grid(row=7, column=3)

# btn rotate
btn_rotate = tk.Button(root, text="Vector rotation", command=rotate_vector)
btn_rotate.grid(row=8, column=0, columnspan=4)

root.mainloop()
