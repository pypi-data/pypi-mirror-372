#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2024

import pytest

from streamsets.sdk.utils import get_random_string


@pytest.fixture(scope='function')
def sample_project(sch):
    builder = sch.get_project_builder()
    project = builder.build(f'project-name-{get_random_string()}')
    sch.add_project(project)

    try:
        yield project
    finally:
        sch.delete_project(project)


@pytest.mark.xfail(reason="Projects feature is not enabled on Dev Control Hub.")
def test_add_project(sch):
    builder = sch.get_project_builder()
    project = builder.build(f'project-name-{get_random_string()}')

    sch.add_project(project)
    try:
        assert project.id is not None
        assert project in sch.projects
    finally:
        sch.delete_project(project)


@pytest.mark.xfail(reason="Projects feature is not enabled on Dev Control Hub.")
def test_delete_project(sch):
    builder = sch.get_project_builder()
    project = builder.build(f'project-name-{get_random_string()}')

    sch.add_project(project)

    assert project.id is not None
    assert project in sch.projects

    sch.delete_project(project)

    assert project not in sch.projects


@pytest.mark.xfail(reason="Projects feature is not enabled on Dev Control Hub.")
def test_add_user_to_project(sample_project, test_user, sch):
    assert test_user not in sample_project.users
    sample_project.add_user(test_user)

    project = sch.projects.get(id=sample_project.id)
    assert project.users.get(id=test_user.id) is not None


@pytest.mark.xfail(reason="Projects feature is not enabled on Dev Control Hub.")
def test_remove_user_from_from_project(sample_project, test_user, sch):
    assert test_user not in sample_project.users
    sample_project.add_user(test_user)

    project = sch.projects.get(id=sample_project.id)
    assert project.users.get(id=test_user.id) is not None

    sample_project.remove_user(test_user)
    project = sch.projects.get(id=sample_project.id)
    with pytest.raises(ValueError):
        project.users.get(id=test_user.id)


@pytest.mark.xfail(reason="Projects feature is not enabled on Dev Control Hub.")
def test_add_group_to_project(sample_project, test_group, sch):
    assert test_group not in sample_project.groups
    sample_project.add_group(test_group)

    project = sch.projects.get(id=sample_project.id)
    assert project.groups.get(group_id=test_group.group_id) is not None


@pytest.mark.xfail(reason="Projects feature is not enabled on Dev Control Hub.")
def test_remove_group_from_from_project(sample_project, test_group, sch):
    assert test_group not in sample_project.groups
    sample_project.add_group(test_group)

    project = sch.projects.get(id=sample_project.id)
    assert project.groups.get(group_id=test_group.group_id) is not None

    sample_project.remove_group(test_group)
    project = sch.projects.get(id=sample_project.id)
    with pytest.raises(ValueError):
        project.groups.get(group_id=test_group.group_id)


@pytest.mark.xfail(reason="Projects feature is not enabled on Dev Control Hub.")
def test_update_project(sample_project, sch):
    original_name = sample_project.name
    original_description = sample_project.description

    new_name = f"new project name {get_random_string()}"
    new_description = f"new project description {get_random_string()}"

    sample_project.name = new_name
    sample_project.description = new_description

    sch.update_project(sample_project)

    assert sample_project.name == new_name
    assert sample_project.description == new_description

    # value error is raised when it cannot find it
    with pytest.raises(ValueError):
        sch.projects.get(name=original_name)
    with pytest.raises(ValueError):
        sch.projects.get(description=original_description)

    assert len(sch.projects.get_all(name=new_name)) == 1
    assert len(sch.projects.get_all(description=new_description)) == 1


@pytest.mark.xfail(reason="Projects feature is not enabled on Dev Control Hub.")
def test_update_user_project_roles(sch, test_user, test_group):
    """Test updating a user's project roles."""
    roles_to_update = ['Engine Administrator', 'Job Operator', 'Pipeline Editor', 'Deployment Manager']
    test_user.project_roles = roles_to_update
    sch.update_user(test_user)

    updated_user = sch.users.get(email_address=test_user.email_address)
    for role in roles_to_update:
        assert role in updated_user.project_roles
    assert len(updated_user.project_roles) == len(roles_to_update)


@pytest.mark.xfail(reason="Projects feature is not enabled on Dev Control Hub.")
def test_update_group_project_roles(sch, test_user, test_group):
    """Test updating a group's assigned roles and membership."""
    try:
        role_to_add = 'Topology User'
        assert test_user not in test_group.users
        assert role_to_add not in test_group.project_roles
        test_group.users.append(test_user)
        test_group.project_roles.append(role_to_add)
        sch.update_group(test_group)
        # update_group updates the in-memory representation directly
        assert test_group.users.get(email_address=test_user.email_address)
        assert role_to_add in test_group.project_roles
    finally:
        # Put the group back to its original state
        # Retrieve the test user again since its definition was updated via role/group addition
        test_group.users.remove(test_user)
        test_group.project_roles.remove(role_to_add)
        sch.update_group(test_group)
        # We expect this to throw a ValueError since the user was removed from the group
        with pytest.raises(ValueError) as value_error:
            test_group.users.get(email_address=test_user.email_address)
        assert value_error
        assert role_to_add not in test_group.project_roles
