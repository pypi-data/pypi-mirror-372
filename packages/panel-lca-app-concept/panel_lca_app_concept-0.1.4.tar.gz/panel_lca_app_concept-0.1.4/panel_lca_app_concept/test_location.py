import panel as pn
import panel_material_ui as pmu

# Test Panel location functionality
pn.extension()

def test_location():
    """Test if Panel location API works"""
    try:
        loc = pn.state.location
        print(f"Location object: {loc}")
        print(f"Has pathname: {hasattr(loc, 'pathname')}")
        print(f"Has search: {hasattr(loc, 'search')}")
        print(f"Has href: {hasattr(loc, 'href')}")
        if hasattr(loc, 'pathname'):
            print(f"Current pathname: {loc.pathname}")
        
        # Test if we can watch location changes
        def on_location_change(event):
            print(f"Location changed: {event}")
        
        if hasattr(loc, 'param'):
            print("Location has param - can watch changes")
            print(f"Location parameters: {list(loc.param)}")
        else:
            print("Location does not have param")
            
    except Exception as e:
        print(f"Error testing location: {e}")

if __name__ == "__main__":
    test_location()