# LiDAR-to-Mesh-for-Blender
## Installation
This is a plugin that can be used to convert LiDAR points to a useable mesh in Blender.  
To install simply download the code into a .zip as shown in the image below.  
![image](https://github.com/user-attachments/assets/6a25252d-6d81-4f76-8ab4-ab4583cc5a93)
<br><br>
Next in Blender go up to Edit and select Preferences... from the drop-down menu.  
![image](https://github.com/user-attachments/assets/fe39069f-2054-4cc0-94b3-c67e86e5de13)
<br><br>
Click on the small arrow in the top right corner and select Install from Disk...  
![image](https://github.com/user-attachments/assets/6e903b79-c9d3-4820-999c-b61889dfef5b)
<br><br>
Browse to where you downloaded the .zip file and select it.  
Next type in "lidar" in the search function and check the box to enable it.  
![image](https://github.com/user-attachments/assets/6d2f1696-3ebf-44db-8174-cc29a22f40e5)  
You should not see a Sidebar enter appear in Blender called Wreckfest (if one didn't already exist) and LiDAR Converter will exist within it.  


## Tool Description
Below is a description of what the UI elements do when you expand the tool in the Blender sidebar.  
<img src="https://github.com/user-attachments/assets/8e90e678-fd69-4c7a-9516-7d3263e5129e" width="184">  

**LiDAR File**: Allows you to select a .las/.laz file containing LiDAR point cloud data.  

**Save Directory**: Allows you to select the folder where the final .blend file will be saved after conversion.  

**PSR Depth**: Controls the Poisson Surface Reconstruction (PSR) Depth, which determines the level of detail in the generated mesh. Higher values result in more detailed terrain at the cost of increased processing time and memory usage. An Ideal value for lower end systems is 8-10, higher end systems can use 11-14, it is not recommended to use anything higher than 14 unless you really need crazy detailed data.  

**Vertex Count**: Defines the target number of vertices after downsampling the point cloud. Lower values speed up processing and reduce file size, while higher values preserve more detail.  

**Scale**: Allows you to adjust the output scale of the terrain after it has been converted. You can manually scale the terrain afetrwards, but this is nice in case you need to get it to a managable size out of the gate.  

**Convert LiDAR to Mesh**: Starts the conversion process. Note that Blender may hang depending on how large your LiDAR file is and how much detail you're trying to get out of it. Just let it run and if you have too much detail, it will error out.  

## Video Tutorial
### [Watch this video on YouTube](https://youtu.be/oP_3GyxefU0)
