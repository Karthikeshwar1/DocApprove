// "Nov 11, 2026, 10:46 PM" in the viewer's locale.
export const formatDate = (iso) =>
  new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
