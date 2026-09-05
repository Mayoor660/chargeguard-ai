export default function TopHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <header className="border-b border-[var(--color-border)] px-8 py-5">
      <h1 className="text-lg font-semibold">{title}</h1>
      {subtitle && <p className="text-sm text-[var(--color-text-secondary)] mt-0.5">{subtitle}</p>}
    </header>
  );
}