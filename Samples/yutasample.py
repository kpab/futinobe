import numpy as np
import matplotlib.pyplot as plt
class Employee:
    def __init__(self,cell_x,cell_y,id,taken_positions):
        while True:
            position=(np.random.randint(cell_x)-0.5,np.random.randint(cell_y)-0.5)
            if position not in taken_positions:
                self.position=position
                break
        self.direction=(0,0)
        self.cell_x=cell_x-0.5
        self.cell_y=cell_y-0.5
        self.id=id
        self.state='red'
        self.encounter_count=0
    def move(self,customers,other_employee_positions):
        nearest_customer_position=self.find_nearest_customer(customers)
        if nearest_customer_position is not None:
            x_diff=nearest_customer_position[0]-self.position[0]
            y_diff=nearest_customer_position[1]-self.position[1]
            if abs(x_diff)>abs(y_diff):
                self.direction=(np.sign(x_diff),0)
            else:
                self.direction=(0,np.sign(y_diff))
        else:
            if self.position[0]==0:
                self.direction=(1,0)
            elif self.position[0]==self.cell_x-1:
                self.direction=(-1,0)
            elif self.position[1]==0:
                self.direction=(0,1)
            elif self.position[1]==self.cell_y-1:
                self.direction=(0,-1)
            else:
                if np.random.rand()>0.5:
                    self.direction=(np.random.choice([-1,1]),0)
                else:
                    self.direction=(0,np.random.choice([-1,1]))
        new_position=(self.position[0]+self.direction[0],self.position[1]+self.direction[1])
        if new_position not in other_employee_positions and 0<=new_position[0]<self.cell_x and 0<=new_position[1]<self.cell_y:
            self.position=new_position
    def find_nearest_customer(self,customers):
        nearest_customer_position=None
        for customer in customers:
            if customer.color=='green':
                continue
            x_diff=abs(customer.position[0]-self.position[0])
            y_diff=abs(customer.position[1]-self.position[1])
            if self.state=='red' and ((x_diff==1 and y_diff==0) or (x_diff==0 and y_diff==1)):
                nearest_customer_position=customer.position
                break
            elif self.state=='black':
                if customer.color=='blue' and ((x_diff==1 and y_diff==0) or (x_diff==0 and y_diff==1)):
                    nearest_customer_position = customer.position
                    break
                elif customer.color=='yellow':
                    possible_positions=[
                        (self.position[0]+dx, self.position[1]+dy)
                        for dx,dy in [(-1,0),(1,0),(0,-1), (0,1)]
                        if (self.position[0]+dx,self.position[1]+dy)!=customer.position
                    ]
                    nearest_customer_position=possible_positions[np.random.randint(len(possible_positions))]
                    break
        return nearest_customer_position
    def update_state(self,customers):
        for customer in customers:
            if customer.position==self.position and customer.color!='green':
                self.encounter_count+=1
                self.state='black' if self.encounter_count%2==1 else 'red'
                break
class Customer:
    def __init__(self,cell_x,cell_y,id):
        self.position=(3.5,3.5)
        self.waiting=True
        self.moving=False
        self.color='blue'
        self.id=id
        self.wait_count=0
        self.employee_visited=False
    def move(self,employee_positions):
        if self.waiting:
            if self.position in employee_positions:
                self.wait_count+=1
                self.employee_visited=True
            elif self.employee_visited:
                self.color='yellow'
                self.employee_visited=False
            if self.wait_count==2:
                self.waiting=False
                self.moving=True
        elif self.moving:
            x_diff=-self.position[0]
            y_diff=-self.position[1]
            if abs(x_diff)>abs(y_diff):
                self.position=(self.position[0]+np.sign(x_diff),self.position[1])
            elif abs(y_diff)>0:
                self.position=(self.position[0],self.position[1]+np.sign(y_diff))
            self.color='green'
            if self.position==(0,0):
                self.moving=False
                self.waiting=True
                self.color='blue'
                self.wait_count=0
cell_x,cell_y=6,6
num_employees=2
taken_positions=set()
employees=[Employee(cell_x,cell_y,id=f'e{i+1}',taken_positions=taken_positions) for i in range(num_employees)]
taken_positions.update(employee.position for employee in employees)
fig,ax=plt.subplots(figsize=(6,6))
ax.set_xlim(0,cell_x-1)
ax.set_ylim(0,cell_y-1)
ax.set_xticks([0.5,1.5])
ax.set_yticks(np.arange(0.5,cell_y+0.5,1))
ax.grid(True)
employee_scatters=[ax.scatter(employee.position[0],employee.position[1],color='red',s=100) for employee in employees]
customers=[]
customer_id=1
new_customer_position=(3.5,3.5)
for frame in range(1000):
    employee_positions=[employee.position for employee in employees]
    for employee in employees:
        other_employee_positions=[pos for pos in employee_positions if pos != employee.position]
        employee.move(customers,other_employee_positions)
        employee_positions=[employee.position for employee in employees]
    if np.random.rand()<0.3 and all(customer.position!=new_customer_position for customer in customers):
        new_customer=Customer(cell_x, cell_y,id=f'c{customer_id}')
        customers.append(new_customer)
        customer_id+=1
    for customer in customers:
        employee_positions=[employee.position for employee in employees]
        customer.move(employee_positions)
    for employee in employees:
        if employee.position in [customer.position for customer in customers]:
            employee.update_state(customers)
    i=0
    while i<len(customers):
        if customers[i].position==(0,0):
            del customers[i]
        else:
            i+=1
    ax.clear()
    ax.set_xlim(0,cell_x-1)
    ax.set_ylim(0,cell_y-1)
    ax.set_xticks(np.arange(0.5,cell_x+0.5,1))
    ax.set_yticks(np.arange(0.5,cell_y+0.5,1))
    ax.grid(True)
    for scatter,employee in zip(employee_scatters,employees):
        scatter.set_offsets(employee.position)
        ax.scatter(employee.position[0],employee.position[1],color=employee.state,s=100)
        ax.text(employee.position[0],employee.position[1],employee.id,color='black',fontsize=20,ha='center',va='center')
    for customer in customers:  
        ax.scatter(customer.position[0],customer.position[1],color=customer.color,s=10000)
        ax.text(customer.position[0],customer.position[1],customer.id,color='black',fontsize=20,ha='center',va='center')
    plt.pause(1.0)
plt.show()