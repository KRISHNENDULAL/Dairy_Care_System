from ..models import Users_table, Order_table
from django.db.models import Count, Q
from geopy.distance import geodesic

class DeliveryAssignment:
    @staticmethod
    def get_delivery_agent_with_least_orders():
        """Get the delivery agent who has the least number of active orders"""
        try:
            # Get all delivery agents with their active order counts
            delivery_agents = Users_table.objects.filter(role='employee').annotate(
                active_orders=Count(
                    'order_table',
                    filter=Q(
                        order_table__status__in=['Pending', 'Confirmed', 'Shipped', 'Out']
                    )
                )
            ).order_by('active_orders')  # Order by number of active orders

            # Get the delivery agent with least orders
            if delivery_agents.exists():
                return delivery_agents.first()
            return None

        except Exception as e:
            print(f"Error getting delivery agent: {str(e)}")
            return None

    @staticmethod
    def get_nearest_delivery_agent(customer_pincode):
        """Get the delivery agent whose pincode is nearest to the customer's pincode"""
        try:
            # First, check if there is a delivery agent with the exact pincode
            delivery_agents = Users_table.objects.filter(role='employee')
            exact_match = delivery_agents.filter(pincode=customer_pincode).first()
            if exact_match:
                return exact_match  # Return the exact match if found

            # If no exact match, proceed to find the nearest agent
            customer_coordinates = DeliveryAssignment.get_coordinates_from_pincode(customer_pincode)
            nearest_agent = None
            min_distance = float('inf')

            for agent in delivery_agents:
                agent_coordinates = DeliveryAssignment.get_coordinates_from_pincode(agent.pincode)
                if agent_coordinates != (0, 0):  # Ensure valid coordinates
                    distance = geodesic(customer_coordinates, agent_coordinates).kilometers
                    if distance < min_distance:
                        min_distance = distance
                        nearest_agent = agent

            return nearest_agent

        except Exception as e:
            print(f"Error getting nearest delivery agent: {str(e)}")
            return None

    @staticmethod
    def auto_assign_delivery_agent(order):
        """Automatically assign a delivery agent to the order based on nearest pincode"""
        try:
            # Get the nearest delivery agent based on the customer's pincode
            nearest_agent = DeliveryAssignment.get_nearest_delivery_agent(order.pincode)
            
            if nearest_agent:
                # Assign the delivery agent and update order status
                order.deliveryboy = nearest_agent
                order.status = "Confirmed"
                order.save()
                
                # Create notification for delivery boy
                from ..models import Notifications_table
                Notifications_table.objects.create(
                    message=f"New order #{order.id} has been assigned to you.",
                    order=order,
                    user=nearest_agent
                )
                return True
            
            return False
            
        except Exception as e:
            print(f"Error assigning delivery agent: {str(e)}")
            return False

    @staticmethod
    def get_coordinates_from_pincode(pincode):
        """Convert pincode to geographical coordinates (latitude, longitude)"""
        # Add your actual pincode mappings here
        pincode_coordinates = {
            '682001': (9.9312, 76.2673),  # Kochi
            '682002': (9.9342, 76.2711),
            '682003': (9.9370, 76.2831),
            '682004': (9.9312, 76.2873),
            '682005': (9.9401, 76.2711),
            # Add all your relevant pincodes and their coordinates
        }
        
        # If pincode not found, try to find nearest available pincode
        if pincode not in pincode_coordinates:
            closest_pincode = min(pincode_coordinates.keys(), 
                                key=lambda x: abs(int(x) - int(pincode)))
            return pincode_coordinates[closest_pincode]
        
        return pincode_coordinates.get(pincode) 