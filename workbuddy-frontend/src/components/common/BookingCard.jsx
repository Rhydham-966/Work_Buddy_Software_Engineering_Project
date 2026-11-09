import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { Calendar, User, Wrench, IndianRupee, Clock } from 'lucide-react'

export function BookingCard({ booking, actions }) {
  return (
    <Card className="p-5" hover>
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <h4 className="font-semibold text-surface-900 dark:text-surface-100">
            {booking.service_name || `Booking #${booking.id}`}
          </h4>
          <p className="text-xs text-surface-400 mt-0.5">ID: #{booking.id}</p>
        </div>
        <Badge status={booking.status}>{booking.status}</Badge>
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm text-surface-600 dark:text-surface-400 mb-5">
        {booking.professional_name && (
          <div className="flex items-center gap-1.5">
            <User size={14} className="text-primary-400" />
            <span>{booking.professional_name}</span>
          </div>
        )}
        {booking.customer_name && (
          <div className="flex items-center gap-1.5">
            <User size={14} className="text-primary-400" />
            <span>{booking.customer_name}</span>
          </div>
        )}
        {booking.scheduled_datetime && (
          <div className="flex items-center gap-1.5">
            <Calendar size={14} className="text-primary-400" />
            <span>{new Date(booking.scheduled_datetime).toLocaleDateString()}</span>
          </div>
        )}
        {booking.total_price && (
          <div className="flex items-center gap-1.5">
            <IndianRupee size={14} className="text-accent-500" />
            <span className="font-medium">₹{booking.total_price}</span>
          </div>
        )}
        {booking.booking_type && (
          <div className="flex items-center gap-1.5">
            <Clock size={14} className="text-primary-400" />
            <span className="capitalize">{booking.booking_type}</span>
          </div>
        )}
        {booking.payment_method && (
          <div className="flex items-center gap-1.5">
            <Wrench size={14} className="text-primary-400" />
            <span className="capitalize">{booking.payment_method}</span>
          </div>
        )}
      </div>

      {actions && (
        <div className="flex flex-wrap gap-2 pt-4 border-t border-surface-100 dark:border-surface-700">
          {actions}
        </div>
      )}
    </Card>
  )
}
