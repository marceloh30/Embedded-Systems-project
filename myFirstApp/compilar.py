from multiprocessing import Pool
import os           
import subprocess



#output1 = subprocess.run(["python3", "app.py"], stdout=subprocess.PIPE)
#output2 = subprocess.run(["python3", "alarma.py"], stdout=subprocess.PIPE)
#output3 = subprocess.run(["python3", "lecturaAnalogica.py", "T"], stdout=subprocess.PIPE)


os.system('python3 app.py & python3 alarma.py & python3 lecturaAnalogica.py T')


# Creating the tuple of all the processes which can be run in parallel
#all_parallel_processes = ('app.py', 'alarma.py', 'lecturaAnalogica.py T')     
                                                                                                               
#next_run = ('script_D.py')
                                                  
# This block of code enables us to call the script from command line.                                                                                
#def execute(process):                                                             
#    os.system(f'python {process}')                                       
                                                                                
                                                                                
#process_pool = Pool(processes = 3)                                                        
#process_pool.map(execute, all_parallel_processes)
#process_pool.map(execute, next_run)