from ..models import Users_table, Order_table
from django.db.models import Count, Q

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
    def auto_assign_delivery_agent(order):
        """Automatically assign a delivery agent to the order"""
        try:
            # Get delivery agent with least orders
            delivery_agent = DeliveryAssignment.get_delivery_agent_with_least_orders()
            
            if delivery_agent:
                # Assign the delivery agent and update order status
                order.deliveryboy = delivery_agent
                order.status = "Confirmed"  # Set initial status
                order.save()
                
                # Create notification for delivery boy
                from ..models import Notifications_table
                Notifications_table.objects.create(
                    message=f"New order #{order.id} has been assigned to you.",
                    order=order,
                    user=delivery_agent
                )
                return True
                
            return False
            
        except Exception as e:
            print(f"Error assigning delivery agent: {str(e)}")
            return False 