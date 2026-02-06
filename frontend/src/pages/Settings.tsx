import { useState } from 'react';
import { Plus, X, Save, AlertCircle, Check } from 'lucide-react';
import {
  useProfile,
  useUpdateProfile,
  useTechStackSuggestions,
  useVendors,
  useAddTechStack,
  useRemoveTechStackItem,
} from '../api/hooks';
import type { TechStackSuggestion } from '../types';

const COLOR_MAP: Record<string, { bg: string; text: string; border: string; selected: string }> = {
  purple: { bg: 'bg-purple-100', text: 'text-purple-800', border: 'border-purple-200', selected: 'bg-purple-600' },
  emerald: { bg: 'bg-emerald-100', text: 'text-emerald-800', border: 'border-emerald-200', selected: 'bg-emerald-600' },
  amber: { bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-200', selected: 'bg-amber-600' },
};

function ProfileTagSection({
  title,
  description,
  items,
  suggestions,
  onToggle,
  colorClass,
}: {
  title: string;
  description: string;
  items: string[];
  suggestions?: TechStackSuggestion[];
  onToggle: (name: string) => void;
  colorClass: string;
}) {
  const colors = COLOR_MAP[colorClass] || COLOR_MAP.purple;

  return (
    <section className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">{title}</h2>
      <p className="text-sm text-gray-600 mb-4">{description}</p>

      {/* Current selections */}
      {items.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {items.map((item) => (
            <span
              key={item}
              className={`inline-flex items-center gap-1 px-3 py-1.5 ${colors.bg} ${colors.text} rounded-full text-sm font-medium`}
            >
              {item}
              <button onClick={() => onToggle(item)} className="hover:opacity-70">
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Suggestions */}
      {suggestions && (
        <div className="flex flex-wrap gap-2">
          {suggestions.map((s) => {
            const isSelected = items.includes(s.name);
            return (
              <button
                key={s.name}
                onClick={() => onToggle(s.name)}
                title={s.description}
                className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                  isSelected
                    ? `${colors.selected} text-white border-transparent`
                    : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                }`}
              >
                {isSelected && <Check className="w-3 h-3 inline mr-1" />}
                {s.name}
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}

export function Settings() {
  const { data: profile, isLoading, error } = useProfile();
  const { data: suggestions } = useTechStackSuggestions();
  const { data: availableVendors } = useVendors();

  const updateProfile = useUpdateProfile();
  const addTechStack = useAddTechStack();
  const removeTechStackItem = useRemoveTechStackItem();

  const [newTech, setNewTech] = useState('');
  const [selectedVendors, setSelectedVendors] = useState<string[]>([]);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Initialize selected vendors from profile
  useState(() => {
    if (profile?.preferred_vendors) {
      setSelectedVendors(profile.preferred_vendors);
    }
  });

  const handleAddTech = async () => {
    if (!newTech.trim()) return;

    try {
      await addTechStack.mutateAsync([newTech.trim().toLowerCase()]);
      setNewTech('');
    } catch (error) {
      console.error('Failed to add tech:', error);
    }
  };

  const handleRemoveTech = async (tech: string) => {
    try {
      await removeTechStackItem.mutateAsync(tech);
    } catch (error) {
      console.error('Failed to remove tech:', error);
    }
  };

  const handleToggleVendor = (vendor: string) => {
    setSelectedVendors((prev) =>
      prev.includes(vendor) ? prev.filter((v) => v !== vendor) : [...prev, vendor]
    );
  };

  const handleSaveVendors = async () => {
    try {
      await updateProfile.mutateAsync({ preferred_vendors: selectedVendors });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
    } catch (error) {
      console.error('Failed to save vendors:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Error loading settings</h2>
        <p className="text-gray-600">
          {error instanceof Error ? error.message : 'Failed to load profile'}
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Settings</h1>

      {/* Tech Stack Section */}
      <section className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Tech Stack</h2>
        <p className="text-sm text-gray-600 mb-4">
          Add technologies you use. Articles related to these will be prioritized in your feed.
        </p>

        {/* Current tech stack */}
        <div className="flex flex-wrap gap-2 mb-4">
          {profile?.tech_stack.map((tech) => (
            <span
              key={tech}
              className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
            >
              {tech}
              <button
                onClick={() => handleRemoveTech(tech)}
                className="hover:text-blue-900"
                disabled={removeTechStackItem.isPending}
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
          {profile?.tech_stack.length === 0 && (
            <span className="text-sm text-gray-500 italic">No technologies added yet</span>
          )}
        </div>

        {/* Add new tech */}
        <div className="flex gap-2 mb-6">
          <input
            type="text"
            value={newTech}
            onChange={(e) => setNewTech(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAddTech()}
            placeholder="Add technology (e.g., lambda, kubernetes)"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={handleAddTech}
            disabled={!newTech.trim() || addTechStack.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add
          </button>
        </div>

        {/* Suggestions */}
        {suggestions && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">Suggestions</h3>
            <div className="space-y-4">
              {Object.entries(suggestions).filter(([category]) => !['domains', 'roles', 'goals'].includes(category)).map(([category, items]) => (
                <div key={category}>
                  <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                    {category}
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {items.map((item) => {
                      const isAdded = profile?.tech_stack.includes(item.name);
                      return (
                        <button
                          key={item.name}
                          onClick={() => !isAdded && addTechStack.mutate([item.name])}
                          disabled={isAdded || addTechStack.isPending}
                          title={item.description}
                          className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                            isAdded
                              ? 'bg-green-50 text-green-700 border-green-200 cursor-default'
                              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                          }`}
                        >
                          {isAdded && <Check className="w-3 h-3 inline mr-1" />}
                          {item.name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Preferred Vendors Section */}
      <section className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Preferred Vendors</h2>
        <p className="text-sm text-gray-600 mb-4">
          Select vendors whose updates you want to prioritize.
        </p>

        <div className="flex flex-wrap gap-3 mb-4">
          {availableVendors?.map((vendor) => {
            const isSelected =
              selectedVendors.includes(vendor) || profile?.preferred_vendors.includes(vendor);
            return (
              <button
                key={vendor}
                onClick={() => handleToggleVendor(vendor)}
                className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                  isSelected
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-blue-300'
                }`}
              >
                {vendor}
              </button>
            );
          })}
        </div>

        <button
          onClick={handleSaveVendors}
          disabled={updateProfile.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {saveSuccess ? (
            <>
              <Check className="w-4 h-4" />
              Saved!
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Save Preferences
            </>
          )}
        </button>
      </section>

      {/* Domains Section */}
      <ProfileTagSection
        title="Domains"
        description="Select your areas of expertise or interest. This helps personalize article analysis."
        items={profile?.domains || []}
        suggestions={suggestions?.domains}
        onToggle={(name) => {
          const current = profile?.domains || [];
          const updated = current.includes(name)
            ? current.filter((d) => d !== name)
            : [...current, name];
          updateProfile.mutate({ domains: updated });
        }}
        colorClass="purple"
      />

      {/* Roles Section */}
      <ProfileTagSection
        title="Roles"
        description="Select your engineering roles. Articles will be analyzed with your role context."
        items={profile?.roles || []}
        suggestions={suggestions?.roles}
        onToggle={(name) => {
          const current = profile?.roles || [];
          const updated = current.includes(name)
            ? current.filter((r) => r !== name)
            : [...current, name];
          updateProfile.mutate({ roles: updated });
        }}
        colorClass="emerald"
      />

      {/* Goals Section */}
      <ProfileTagSection
        title="Goals"
        description="Select your current goals. Article relevance and insights will be tailored to these."
        items={profile?.goals || []}
        suggestions={suggestions?.goals}
        onToggle={(name) => {
          const current = profile?.goals || [];
          const updated = current.includes(name)
            ? current.filter((g) => g !== name)
            : [...current, name];
          updateProfile.mutate({ goals: updated });
        }}
        colorClass="amber"
      />

      {/* LLM Provider Section */}
      <section className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">LLM Provider</h2>
        <p className="text-sm text-gray-600 mb-4">
          Select which CLI tool to use for article processing.
        </p>

        <div className="space-y-2">
          {['claude', 'copilot', 'none'].map((provider) => (
            <label
              key={provider}
              className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
            >
              <input
                type="radio"
                name="llm_provider"
                value={provider}
                checked={profile?.llm_provider === provider}
                onChange={() => updateProfile.mutate({ llm_provider: provider })}
                className="w-4 h-4 text-blue-600"
              />
              <div>
                <div className="font-medium text-gray-900 capitalize">
                  {provider === 'claude'
                    ? 'Claude Code'
                    : provider === 'copilot'
                    ? 'GitHub Copilot CLI'
                    : 'None'}
                </div>
                <div className="text-sm text-gray-500">
                  {provider === 'claude'
                    ? 'Use Claude Code CLI for article processing'
                    : provider === 'copilot'
                    ? 'Use GitHub Copilot CLI for article processing'
                    : 'Disable LLM processing'}
                </div>
              </div>
            </label>
          ))}
        </div>
      </section>
    </div>
  );
}
