import { useState, useEffect } from 'react'
import { Briefcase } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { ServiceCard }  from '../../components/common/ServiceCard'
import { SearchInput }  from '../../components/ui/SearchInput'
import { SkeletonGrid } from '../../components/ui/Skeleton'
import { EmptyState }   from '../../components/ui/EmptyState'
import { Pagination }   from '../../components/ui/Pagination'
import { getServices }  from '../../services/customerService'
import { useDebounce }  from '../../hooks/useDebounce'
import { usePagination } from '../../hooks/usePagination'
import toast from 'react-hot-toast'

export default function ServicesPage() {
  const [services, setServices] = useState([])
  const [loading, setLoading]   = useState(true)
  const [search, setSearch]     = useState('')

  const debounced = useDebounce(search, 300)

  useEffect(() => {
    getServices()
      .then(r => setServices(r.data.services || []))
      .catch(() => toast.error('Failed to load services'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = services.filter(s =>
    s.name?.toLowerCase().includes(debounced.toLowerCase()) ||
    s.description?.toLowerCase().includes(debounced.toLowerCase())
  )

  const { paged, page, totalPages, next, prev, goTo } = usePagination(filtered, 9)

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="page-title mb-1">Browse Services</h1>
        <p className="text-surface-500 text-sm">Find the right professional for every job</p>
      </div>

      {/* Search */}
      <div className="mb-6 flex gap-3">
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Search services..."
          className="flex-1 max-w-md"
        />
        {search && (
          <button onClick={() => setSearch('')}
            className="text-sm text-primary-600 font-medium hover:underline px-2">
            Clear
          </button>
        )}
      </div>

      {loading ? (
        <SkeletonGrid count={9} />
      ) : paged.length === 0 ? (
        <EmptyState
          icon={Briefcase}
          title="No services found"
          description={debounced ? `No results for "${debounced}"` : 'No services available right now.'}
        />
      ) : (
        <>
          <p className="text-sm text-surface-500 mb-4">{filtered.length} service{filtered.length !== 1 ? 's' : ''} found</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {paged.map(s => <ServiceCard key={s.id} service={s} />)}
          </div>
          <Pagination page={page} totalPages={totalPages} onPrev={prev} onNext={next} onGoTo={goTo} />
        </>
      )}
    </DashboardLayout>
  )
}
