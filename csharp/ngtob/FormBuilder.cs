namespace BlazorApp
{
  public abstract class AbstractControl<TValue>
  {
    public TValue Value { get; set; }
    // ... other properties and methods
  }
  public class FormGroup<TControls> : AbstractControl<Dictionary<string, AbstractControl<object>>>
  {
    // ... other properties and methods
  }

  public class FormBuilder
  {
    private readonly IServiceProvider _serviceProvider;

    public FormBuilder(IServiceProvider serviceProvider)
    {
      _serviceProvider = serviceProvider;
    }

    public FormGroup<TControls> Group<TControls>(TControls controls)
        where TControls : class, new()
    {
      // ... create a new FormGroup
      return new FormGroup<TControls>();
    }

    // ... other methods
  }
}
